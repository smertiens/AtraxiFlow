from nodes.TextResource import *
import tkinter as tk
from tkinter import simpledialog

class GUIInputNode(InputNode):
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
        return 'GUIInputNode'

    def run(self, stream):
        self.mergeProperties()

        wnd = tk.Tk()
        userInput = simpledialog.askstring("Input", self.getProperty("prompt"), parent=wnd)

        if userInput == None:
            userInput = ""

        stream.add_resource(TextResource(self.getProperty('save_to', 'last_cli_input'), {"text": userInput}))