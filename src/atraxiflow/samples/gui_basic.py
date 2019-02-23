#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.gui import *
from atraxiflow.core.stream import *
from atraxiflow.nodes.gui import GUIFormInputNode
from atraxiflow.nodes.common import *
st = Stream()

form_node = GUIFormInputNode({
    'fields': {
        'greeting': Combobox('Greeting', items=['Hello', 'Cheerio']),
        'name': Textfield('Name')
    },
    'text': 'How should I greet you?',
    'window': Window(title='Greeting')
})
out_node = EchoOutputNode({'msg': '{Text:greeting}, {Text:name}!'})

st >> form_node >> out_node

gui = GUI(st)
gui.flow()