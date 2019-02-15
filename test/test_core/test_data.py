#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.core.data import StringValueProcessor, dict_read_from_path
from atraxiflow.core.exceptions import ValueException
from atraxiflow.core.stream import Stream
from atraxiflow.nodes.text import TextResource


class TestData:

    def get_stream_for_test(self):
        st = Stream()
        st.add_resource(TextResource("text1", {"text": "one"}))
        st.add_resource(TextResource("text2", {"text": "two"}))
        return st

    def test_find_vars_and_replace_simple(self):
        p = StringValueProcessor(Stream())
        p.add_variable("demo", "omed")
        p.add_variable("one", "eno")
        p.add_variable("two", "owt")
        out = p.parse("Hello World {demo} and  another {one}, {two}.")

        assert "Hello World omed and  another eno, owt." == out

    def test_find_vars_and_replace_resource(self):
        st = self.get_stream_for_test()
        p = StringValueProcessor(st)
        p.add_variable("demo", "omed")

        out = p.parse("Hello World {demo} and  another {Text:text1}, {Text:text2}.")
        assert "Hello World omed and  another one, two." == out

    def test_find_in_dict_by_path(self):
        d = {
            'hello': {
                'world': 123
            },
            'foo': {
                'bar': {
                    'even': 'deeper'
                }
            }
        }

        assert 123 == dict_read_from_path(d, 'hello.world')
        assert 'deeper' == dict_read_from_path(d, 'foo.bar.even')
        assert {'world': 123} == dict_read_from_path(d, 'hello')

        with pytest.raises(ValueException):
            dict_read_from_path(d, 'hello.adasdada')
