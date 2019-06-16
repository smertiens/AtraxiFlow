#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core import *
from atraxiflow.base.text import TextValidatorNode
from atraxiflow.base.common import NullNode
from atraxiflow.base.resources import TextResource


def test_rule_not_empty():
    node = TextValidatorNode({
        'rules': {
            'not_empty': {}
        }
    })

    out_node = NullNode()
    out_node.output.add(TextResource('Hello World'))

    assert Workflow.create([out_node, node]).run()

    out_node.output.clear()
    out_node.output.add(TextResource(''))

    assert not Workflow.create([out_node, node]).run()


def test_rule_max_len():
    node = TextValidatorNode({
        'rules': {
            'max_len': {'length': 5}
        }
    })

    out_node = NullNode()
    out_node.output.add(TextResource('Hello World'))

    assert not Workflow.create([out_node, node]).run()

    out_node.output.clear()
    out_node.output.add(TextResource('Hello'))

    assert Workflow.create([out_node, node]).run()


def test_rule_min_len():
    node = TextValidatorNode({
        'rules': {
            'min_len': {'length': 10}
        }
    })

    out_node = NullNode()
    out_node.output.add(TextResource('Hello World'))

    assert Workflow.create([out_node, node]).run()

    out_node.output.clear()
    out_node.output.add(TextResource('Hello'))

    assert not Workflow.create([out_node, node]).run()


def test_rule_regex_must_not_match():
    node = TextValidatorNode({
        'rules': {
            'regex': {
                'pattern': r'\w+\s+\w+!',
                'mode': 'must_not_match'
            }
        }
    })

    out_node = NullNode()
    out_node.output.add(TextResource('Hello World!'))

    assert not Workflow.create([out_node, node]).run()

    out_node.output.clear()
    out_node.output.add(TextResource('HelloWorld'))

    assert Workflow.create([out_node, node]).run()


def test_rule_regex_must_match():
    node = TextValidatorNode({
        'sources': 'Text:neg',
        'rules': {
            'regex': {
                'pattern': r'\w+\s+\w+!',
                'mode': 'must_match'
            }
        }
    })

    out_node = NullNode()
    out_node.output.add(TextResource('Hello World!'))

    assert Workflow.create([out_node, node]).run()

    out_node.output.clear()
    out_node.output.add(TextResource('HelloWorld'))

    assert not Workflow.create([out_node, node]).run()
