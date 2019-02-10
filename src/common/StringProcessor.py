from Stream import Stream
import re


class StringProcessor:

    def __init__(self, stream):
        """

        :type stream: Stream
        """
        self.stream = stream
        self._value_map = {}

    def addVariable(self, key, value):
        self._value_map[key] = value

    def parse(self, string):
        """

        :type string: str
        """

        matches = re.findall("{(.+?)}", string)

        for match in matches:
            string = string.replace("{" + match + "}", self.getVariableValue(match))

        return string

    def getVariableValue(self, var):
        """

        :type var: str
        """
        try:
            (namespace, key) = var.split("::")
        except ValueError:
            if var in self._value_map:
                return self._value_map[var]
            else:
                return ""

        if namespace == "Res":
            res = self.stream.getResource(key)

            if "toString" in dir(res):
                return res.toString()
            else:
                return ""
