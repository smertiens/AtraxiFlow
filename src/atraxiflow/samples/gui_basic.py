#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.stream import *
from atraxiflow.nodes.gui import *

st = Stream()

form_node = GUIFormInputNode({
    'fields': {
        'greeting': Combobox('Greeting', items=['Hello', 'Cheerio']),
        'name': Textfield('Name')
    },
    'text': 'How should I greet you?',
    'window': Window(title='Greeting')
})
out_node = GUIMessageNode({'title': 'Greeting', 'text': '{Text:greeting}, {Text:name}'})

st >> form_node >> out_node >> flow_ui()

# gui = GUI(st)
# gui.flow()
