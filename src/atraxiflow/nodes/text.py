#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import logging
import re

from atraxiflow.nodes.foundation import *


class TextResource(Resource):
    '''
    A resource holding a text
    '''

    def __init__(self, name="", props=None):
        self._known_properties = {
            'text': {
                'label': "Text",
                'type': "string",
                'required': False,
                'hint': 'A simple text',
                'default': '',
                'creator:multiline': True
            }
        }

        self._listeners = {}
        self._stream = None
        self.name, self.properties = self.get_properties_from_args(name, props)

    def get_prefix(self):
        return 'Text'

    def get_data(self):
        return self.get_property('text', '')

    def update_data(self, text):
        self.set_property('text', text)

    def __str__(self):
        return str(self.get_property('text', ''))


class TextFileInputNode(InputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'filename': {
                'label': 'Filename',
                'type': 'file',
                'required': True,
                'hint': 'The filename to read from'
            },
            'resource_name': {
                'label': 'Resource name',
                'type': 'string',
                'required': False,
                'hint': 'The name of the resource the file contents should be saved to',
                'default': 'last_textfile_contents'
            }
        }
        self._listeners = {}

        self.name, self.properties = self.get_properties_from_args(name, props)
        self._out = None

    def run(self, stream):
        self.check_properties()

        try:
            with open(self.get_property('filename'), 'r') as f:
                res = TextResource(self.get_property('resource_name'), {'text': f.read()})
                stream.add_resource(res)
                self._out = res

        except IOError:
            stream.get_logger().error('Could not open file "{0}"'.format(self.get_property('filename')))
            return False

        return True

    def get_output(self):
        return self._out


class TextFileOutputNode(OutputNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'sources': {
                'label': 'Sources',
                'type': "resource_query",
                'required': False,
                'hint': 'The resource query to obtain TextResources that should be written to file',
                'default': 'Text:*'
            },
            'filename': {
                'label': 'Filename',
                'type': 'file',
                'required': True,
                'hint': 'The filename to write to'
            },
            'newline_per_res': {
                'label': 'Add newline after each resource',
                'type': "bool",
                'required': False,
                'hint': 'When writing multiple resources, a newline will be added after each resources output',
                'default': True
            }
        }
        self._listeners = {}

        self.name, self.properties = self.get_properties_from_args(name, props)
        self._out = None

    def run(self, stream):
        self.check_properties()

        try:
            with open(self.get_property('filename'), 'w') as f:
                resources = stream.get_resources(self.get_property('sources'))

                for res in resources:
                    f.write(res.get_data())
                    if self.get_property('newline_per_res') is True:
                        f.write('\n')

        except IOError:
            stream.get_logger().error('Could not open file "{0}"'.format(self.get_property('filename')))
            return False

        return True

    def get_output(self):
        return self._out


class TextValidatorNode(ProcessorNode):
    '''
    Offers different rules to validate a text
    '''

    def __init__(self, name="", props=None):
        self._known_properties = {
            'sources': {
                'label': 'Sources',
                'type': "resource_query",
                'required': False,
                'hint': 'The resource query to obtain TextResources to check',
                'default': 'Text:*'
            },
            'rules': {
                'label': 'Rules',
                'type': "list",
                'creator:list_item_fields': [
                    {
                        'name': 'rule',
                        'label': 'Rule',
                        'type': 'combobox',
                        'value': ['not_empty', 'min_len', 'max_len', 'regex']
                    },
                    {
                        'name': 'param1',
                        'label': 'Param 1',
                        'type': 'text',
                        'value': ''
                    }
                ],
                'creator:list_item_formatter': self.format_list_item,
                'required': False,
                'hint': 'A list of validation rules',
                'default': {}
            }
        }
        self._listeners = {}
        self._stream = None
        self.name, self.properties = self.get_properties_from_args(name, props)
        self._out = []

    def format_list_item(self, format, data):

        if format == 'list_item':
            if data['rule'] == 'not_empty':
                return '{0}'.format(data['rule'])
            elif data['rule'] == 'min_len':
                return 'At least {0} characters'.format(data['param1'])
            elif data['rule'] == 'max_len':
                return 'Not more than {0} characters'.format(data['param1'])
            elif data['rule'] == 'regex':
                return 'Regular expression: "{0}"'.format(data['param1'])

        elif format == 'store':
            return data
        elif format == 'node_value':
            if isinstance(data, list):
                out = {}
                for row in data:
                    if row['rule'] == 'not_empty':
                        out[row['rule']] = {}
                    elif row['rule'] == 'min_len' or row['rule'] == 'max_len':
                        out[row['rule']] = {'length': row['param1']}
                    elif row['rule'] == 'regex':
                        out[row['rule']] = {'pattern': row['param1']}

                return out

    def get_output(self):
        return self._out

    def _rule_not_empty(self, text, params=[]):
        if text == '' or text is None:
            return False

        return True

    def _rule_min_len(self, text, params=[]):
        if not 'length' in params:
            self._stream.get_logger().error('Rule min_len: Missing parameter "length"')
            return False

        length = int(params['length'])
        return len(text) >= length

    def _rule_max_len(self, text, params=[]):
        if not 'length' in params:
            self._stream.get_logger().error('Rule max_len: Missing parameter "length"')
            return False

        length = int(params['length'])
        return len(text) <= length

    def _rule_regex(self, text, params=[]):
        if not 'pattern' in params:
            self._stream.get_logger().error('Rule regex: Missing parameter "pattern"')
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
                self._stream.get_logger().error('Unrecognized rule: "{0}"'.format(rule))
            else:
                f = getattr(self, "_rule_{0}".format(rule))
                if f(text, params) is False:
                    return False

        return True

    def run(self, stream):
        self._stream = stream
        self.check_properties()

        resources = stream.get_resources(self.get_property('sources'))

        for res in resources:
            if not self._validate(res.get_data(), self.get_property('rules')):
                return False

        return True
