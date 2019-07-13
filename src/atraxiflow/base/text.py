#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import logging
import re

from atraxiflow.core import *
from atraxiflow.properties import *
from atraxiflow.base.resources import TextResource


class TextFileInputNode(Node):
    """
    @Name: Load textfile
    """
    def __init__(self, properties: dict = None):
        node_properties = {
            'filename': Property(expected_type=str, required=True, label='Filename', hint='The filename to read from',
                                 display_options={'role': 'file'})
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

        try:
            with open(self.property('filename').value(), 'r') as f:
                self.output.add(TextResource(f.read()))

        except IOError:
            ctx.get_logger().error('Could not open file "{0}"'.format(self.property('filename').value()))
            return False

        return True


class TextFileOutputNode(Node):
    """
    @Name: Write to textfile
    """
    def __init__(self, properties: dict = None):
        node_properties = {
            'filename': Property(expected_type=str, label='Filename', required=True, hint='The filename to write to'),
            'newline_per_res': Property(expected_type=bool, label='Newline after each resource', required=False,
                                        default=True,
                                        hint='When writing multiple resources, a newline will be added after each resources output')
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        try:
            with open(self.property('filename').value(), 'w') as f:
                resources = self.get_input().find('atraxiflow.TextResource')

                for res in resources:
                    f.write(res.get_value())
                    if self.property('newline_per_res').value() is True:
                        f.write('\n')

        except IOError:
            ctx.get_logger().error('Could not open file "{0}"'.format(self.property('filename').value()))
            return False

        return True


class TextValidatorNode(Node):
    """
    @Name: Validate text
    @Hide: True
    """

    def __init__(self, properties: dict = None):

        node_properties = {
            'rules': Property(expected_type=dict, label='Rules', required=False, hint='A list of validation rules',
                              default={})
        }

        super().__init__(node_properties, properties)

    def _rule_not_empty(self, text, params=None):
        if text == '' or text is None:
            return False

        return True

    def _rule_min_len(self, text, params=None):
        params = [] if params is None else params
        if not 'length' in params:
            self._ctx.get_logger().error('Rule min_len: Missing parameter "length"')
            return False

        length = int(params['length'])
        return len(text) >= length

    def _rule_max_len(self, text, params=None):
        params = [] if params is None else params
        if not 'length' in params:
            self._ctx.get_logger().error('Rule max_len: Missing parameter "length"')
            return False

        length = int(params['length'])
        return len(text) <= length

    def _rule_regex(self, text, params=None):
        params = [] if params is None else params
        if not 'pattern' in params:
            self._ctx.get_logger().error('Rule regex: Missing parameter "pattern"')
            return False

        mode = ''
        pattern = params['pattern']
        if not 'mode' in params:
            mode = 'must_match'
        else:
            mode = params['mode']

        if mode == 'must_match':
            if not re.match(pattern, text):
                return False
        elif mode == 'must_not_match':
            if re.match(pattern, text):
                return False
        return True

    def _validate(self, text, rules):
        '''
        Validates the string using the given rule

        Accepted rules are:

            not_empty
            min_length - Takes one more item: length
            max_length - Takes one more item: length
            regex - Takes two more items: pattern, mode (must_match, must_not_match)

        :param text: str
        :param rules: list
        :return: boolean
        '''

        for rule, params in rules.items():
            if not "_rule_{0}".format(rule) in dir(self):
                self._ctx.get_logger().error('Unrecognized rule: "{0}"'.format(rule))
            else:
                f = getattr(self, "_rule_{0}".format(rule))
                if f(text, params) is False:
                    return False

        return True

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        self._ctx = ctx
        resources = self.get_input().find('atraxiflow.TextResource')

        for res in resources:
            if not self._validate(res.get_value(), self.property('rules').value()):
                return False

        return True
