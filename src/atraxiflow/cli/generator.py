#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import re, os
from PyInquirer import prompt


class TemplateParser:
    TOKEN_CMD_NAME = 'CMD_NAME'
    TOKEN_STRING = 'STRING'
    TOKEN_ARGS = 'ARGS'
    TOKEN_LIST = 'LIST'
    TOKEN_VARIABLE_ASSIGNMENT = 'VARIABLE_ASSIGNMENT'

    def __init__(self, template_dir):

        self._template_dir = template_dir
        # one-dimensional tree for now
        self._parsetree = []

    def parse_template(self, template, return_content = False):
        p = os.path.join(self._template_dir, template)
        if not os.path.exists(p):
            raise FileNotFoundError('No template definition found for template "{0}"'.format(template))

        content = ''
        questions = []
        outfile = ''

        with open(p) as f:
            for line in f:
                if line == '' or not line.startswith('#'):
                    content += line
                    continue

                if line.startswith('#%'):
                    # comment
                    continue

                # remove comment sign
                line = line[1:]
                line = line.lstrip(' ')

                if line.startswith('tpl::'):
                    cmd, args = self._parse_tpl_command(line[len('tpl::'):])

                    if cmd == 'choose':
                        # choose(varname, prompt, choices)
                        questions.append({
                            'type': 'list',
                            'name': args[0][0],
                            'message': args[1][0],
                            'choices': args[2][0]
                        })
                    elif cmd == 'ask':
                        questions.append({
                            'type': 'input',
                            'name': args[0][0],
                            'message': args[1][0]
                        })
                    elif cmd == 'yesno':
                        questions.append({
                            'type': 'confirm',
                            'name': args[0][0],
                            'message': args[1][0],
                            # 'default': False
                        })
                    elif cmd == 'filename':
                        outfile = args[0][0]

                    else:
                        raise AttributeError('Template commmand "{0}" not recognized.'.format(cmd))

                else:
                    content += line

        if outfile == '':
            raise ValueError('No output filename specified in template.')

        answers = prompt(questions)

        for k, v in answers.items():
            if not isinstance(v, str):
                continue

            content = content.replace('${0}'.format(k), v)
            outfile = outfile.replace('${0}'.format(k), v)

        if return_content is True:
            return content, outfile
        else:
            with open(os.path.realpath(os.path.join('.', outfile)), 'w') as f:
                f.write(content)

    def _get_current_token(self):
        return self._parsetree[-1]

    def _has_upstream_token(self, token):
        if len(self._parsetree) < 2:
            return False

        tree = self._parsetree.copy()
        tree.reverse()
        tree = tree[1:]
        for item in tree:
            if item == token:
                return True

        return False

    def _enter_level(self, token):
        self._parsetree.append(token)

    def _leave_level(self):
        del self._parsetree[-1]

    def _parse_tpl_command(self, cmd):
        self._parsetree.clear()
        self._enter_level(self.TOKEN_CMD_NAME)
        cmd_name = ''
        current_arg = ['', 'undefined']
        current_list_item = ''
        current_list = []
        arguments = []

        for pos in range(0, len(cmd)):
            chr = cmd[pos:pos + 1]

            if self._get_current_token() == self.TOKEN_CMD_NAME and chr == '(':
                # Start of argument list
                self._enter_level(self.TOKEN_ARGS)

            elif self._get_current_token() == self.TOKEN_CMD_NAME and chr == '=':
                # command name defines not a function-like object but a simple variable
                self._leave_level()
                self._enter_level(self.TOKEN_VARIABLE_ASSIGNMENT)

            elif self._get_current_token() == self.TOKEN_CMD_NAME:
                # belongs to the command name
                cmd_name += chr

            elif self._get_current_token() == self.TOKEN_STRING and chr == '"':
                # end of string argument
                # we are back in arg list level
                self._leave_level()

            elif chr == '"':
                # start of string argument
                self._enter_level(self.TOKEN_STRING)
                # current_arg[0] += chr
                current_arg[1] = 'string'

            elif chr == ',' and self._get_current_token() != self.TOKEN_STRING:
                if self._get_current_token() == self.TOKEN_ARGS:
                    # next argument coming up
                    arguments.append(current_arg)
                    current_arg = ['', 'undefined']
                elif self._get_current_token() == self.TOKEN_LIST:
                    # add item to list
                    current_list.append(current_list_item)
                    current_list_item = ''

            elif self._get_current_token() == self.TOKEN_ARGS and chr == '(':
                # start of list
                self._enter_level(self.TOKEN_LIST)
                current_list_item = ''
                current_arg[0] = ''
                current_arg[1] = 'list'

            elif self._get_current_token() == self.TOKEN_ARGS and chr == ')':
                # end of command
                arguments.append(current_arg)
                current_arg = ['', 'undefined']

                # leave loop
                break

            ################
            # Process lists
            ################

            elif self._get_current_token() == self.TOKEN_LIST and chr == ')':
                # end of list
                self._leave_level()
                current_list.append(current_list_item)
                current_arg[0] = current_list

            elif self._get_current_token() == self.TOKEN_LIST:
                # just add it to current arg
                current_list_item += chr

            else:
                if chr == '\n':
                    chr = ''
                elif chr == ' ':
                    if self._get_current_token() != self.TOKEN_STRING:
                        continue

                # by default add char to argument, list or variable assignment
                if self._has_upstream_token(self.TOKEN_LIST) or self._get_current_token() == self.TOKEN_LIST:
                    current_list_item += chr

                elif self._has_upstream_token(self.TOKEN_ARGS) or self._get_current_token() == self.TOKEN_ARGS:
                    current_arg[0] += chr
                elif self._has_upstream_token(
                        self.TOKEN_VARIABLE_ASSIGNMENT) or self._get_current_token() == self.TOKEN_VARIABLE_ASSIGNMENT:
                    current_arg[0] += chr

            if pos == len(cmd) - 1:
                # EOL
                if self._get_current_token() == self.TOKEN_VARIABLE_ASSIGNMENT:
                    current_arg[1] = 'variable_assignment'
                    arguments.append(current_arg)

            # print(chr, self._get_current_token(), self._parsetree)

        cmd_name = cmd_name.lstrip('\t ').rstrip('\t ')

        return cmd_name, arguments
