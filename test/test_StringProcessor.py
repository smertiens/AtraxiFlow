import unittest
from common.StringProcessor import StringProcessor
from Stream import Stream
from resources.TextResource import TextResource

class test_StringProcessor(unittest.TestCase):

    def test_find_vars_and_replace_simple(self):
        p = StringProcessor(Stream())
        p.addVariable("demo", "omed")
        p.addVariable("one", "eno")
        p.addVariable("two", "owt")
        out = p.parse("Hello World {demo} and  another {one}, {two}.")

        self.assertEqual("Hello World omed and  another eno, owt.", out)

    def test_find_vars_and_replace_resource(self):
        st = Stream()
        st.addResource(TextResource("text1", {"text": "one"}))
        st.addResource(TextResource("text2", {"text": "two"}))
        p = StringProcessor(st)
        p.addVariable("demo", "omed")
        out = p.parse("Hello World {demo} and  another {Res::Text:text1}, {Res::Text:text2}.")

        self.assertEqual("Hello World omed and  another one, two.", out)

if __name__ == '__main__':
    unittest.main()
