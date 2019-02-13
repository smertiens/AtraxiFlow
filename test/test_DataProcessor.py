#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import unittest
from atraxiflow.common.data import StringValueProcessor
from atraxiflow.Stream import Stream
from atraxiflow.nodes.TextResource import TextResource

class test_DataProcessor(unittest.TestCase):

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

        self.assertEqual("Hello World omed and  another eno, owt.", out)

    def test_find_vars_and_replace_resource(self):
        st = self.get_stream_for_test()
        p = StringValueProcessor(st)
        p.add_variable("demo", "omed")

        out = p.parse("Hello World {demo} and  another {Res::text1}, {Res::text2}.")
        self.assertEqual("Hello World omed and  another one, two.", out)

if __name__ == '__main__':
    unittest.main()
