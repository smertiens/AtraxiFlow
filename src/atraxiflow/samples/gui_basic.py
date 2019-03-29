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
        'greeting': Combobox('Greeting', items=['Hello', 'Cheerio'], editable=True),
        'name': Textfield('Name')
    },
    'text': 'How should I greet you?',
    'window': Window(title='Greeting')
})
out_node = GUIMessageNode({'title': 'Greeting', 'text': '{Text:greeting}, {Text:name}'})
st.append_node(form_node)
st.append_node(out_node)

gui = GUIStream.from_stream(st)
#gui.set_autostart(True)

gui.flow()
