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
                'default': ''
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


class TextValidatorNode(ProcessorNode):
    '''
    Offers different rules to validate a text
    '''
    def __init__(self, name="", props=None):
        self._known_properties = {
            'sources': {
                'type': "string",
                'required': False,
                'hint': 'The resource query to obtain TextResources to check',
                'default': 'Text:*'
            },
            'rules': {
                'type': "list",
                'required': False,
                'hint': 'A list of validation rules',
                'default': {}
            }
        }
        self._listeners = {}
        self._stream = None
        self.name, self.properties = self.get_properties_from_args(name, props)

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
            if not "_rule_{}".format(rule) in dir(self):
                self._stream.get_logger().error('Unrecognized rule: "{0}"'.format(rule))
            else:
                f = getattr(self, "_rule_{}".format(rule))
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
