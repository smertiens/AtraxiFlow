#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.stream import Stream
from atraxiflow.nodes.text import TextResource, TextValidatorNode


def test_rule_not_empty():
    text = TextResource('txt', {'text': 'Hello World!'})
    text2 = TextResource('txt_empty', {'text': ''})

    node = TextValidatorNode({
        'sources': 'Text:txt',
        'rules': {
            'not_empty': {}
        }
    })

    st = Stream()
    st.add_resource(text)
    st.add_resource(text2)
    st.append_node(node)
    assert 2 == len(st.get_resources('Text:*'))
    assert st.flow()

    node.set_property('sources', 'Text:txt_empty')

    assert not st.flow()


def test_rule_max_len():
    text = TextResource('long', {'text': 'Hello World!'})
    text2 = TextResource('short', {'text': 'Hello'})

    node = TextValidatorNode({
        'sources': 'Text:short',
        'rules': {
            'max_len': {'length': 5}
        }
    })

    st = Stream()
    st.add_resource(text)
    st.add_resource(text2)
    st.append_node(node)
    assert 2 == len(st.get_resources('Text:*'))
    assert st.flow()

    node.set_property('sources', 'Text:long')

    assert not st.flow()


def test_rule_min_len():
    text = TextResource('long', {'text': 'Hello World!'})
    text2 = TextResource('short', {'text': 'Hello'})

    node = TextValidatorNode({
        'sources': 'Text:long',
        'rules': {
            'min_len': {'length': 10}
        }
    })

    st = Stream()
    st.add_resource(text)
    st.add_resource(text2)
    st.append_node(node)
    assert 2 == len(st.get_resources('Text:*'))
    assert st.flow()

    node.set_property('sources', 'Text:short')

    assert not (st.flow())


def test_rule_regex_must_not_match():
    text = TextResource('pos', {'text': 'Hello World!'})
    text2 = TextResource('neg', {'text': 'HelloWorld'})

    node = TextValidatorNode({
        'sources': 'Text:neg',
        'rules': {
            'regex': {
                'pattern': '\w+\s+\w+!',
                'mode': 'must_not_match'
            }
        }
    })

    st = Stream()
    st.add_resource(text)
    st.add_resource(text2)
    st.append_node(node)
    assert 2 == len(st.get_resources('Text:*'))
    assert st.flow()

    node.set_property('sources', 'Text:pos')

    assert not st.flow()


def test_rule_regex_must_match():
    text = TextResource('neg', {'text': 'Hello World!'})
    text2 = TextResource('pos', {'text': 'HelloWorld'})

    node = TextValidatorNode({
        'sources': 'Text:neg',
        'rules': {
            'regex': {
                'pattern': '\w+\s+\w+!',
                'mode': 'must_match'
            }
        }
    })

    st = Stream()
    st.add_resource(text)
    st.add_resource(text2)
    st.append_node(node)
    assert 2 == len(st.get_resources('Text:*'))
    assert st.flow()

    node.set_property('sources', 'Text:pos')

    assert not st.flow()
