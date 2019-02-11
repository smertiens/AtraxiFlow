from nodes.InputNode import *
from nodes.TextResource import *


class CLIInputNode(InputNode):
    _known_properties = {
        'save_to': {
            'type': "string",
            'required': False,
            'hint': 'THe name of the text resource to save the input to.'
        },
        'prompt': {
            'type': "string",
            'required': False,
            'hint': 'The text to display when prompting the user for input.'
        }
    }

    children = []


    def getNodeClass(self):
        return 'CLIInputNode'

    def run(self, stream):
        self.mergeProperties()

        userInput = input(self.getProperty('prompt', 'Please enter') + ": ")
        stream.add_resource(TextResource(self.getProperty('save_to', 'last_cli_input'), {"text": userInput}))