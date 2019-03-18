GUI nodes
=========

These nodes allow you to collect and output data using a user interface.
In order to use these nodes you need to install Pyside2 (`<https://pypi.org/project/PySide2/>`_).

GUIMessageNode
**************

This node will show a standard message box.

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - title
     - The title of the messagebox *will not ne shown on OSX!*
     - No
   * - text
     - The text you want to present to the user
     - No
   * - icon
     - The icon that is shown in your messagebox (depicting the type of your message). Possible values: info, question, warning, error
     - No. Defaults to "info".


**Output**

This node has no output.


**Example**

.. code-block:: python

    from atraxiflow.core.stream import *
    from atraxiflow.nodes.gui import *

    ui_msg = GUIMessageNode({
        'title': 'Hello World',
        'text': 'This is a message!',
        'icon': 'warning'
    })

    Stream.create() >> ui_msg >> flow()

.. image:: /images/msgbox.png


GUIFormNode
***********

With this node you can easily build a form and use the input values later in your stream (see example).

**Properties**

.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - fields
     - The title of the messagebox *will not ne shown on OSX!*
     - No
   * - window
     - The configuration for the form window. See :ref:`windowhelper`.
     - No
   * - text
     - The icon that is shown in your messagebox (depicting the type of your message). Possible values: info, question, warning, error
     - No. Defaults to "info".
   * - btn_accept_text
     - The text of the accept button
     - No. Defaults to "Okay".
   * - btn_cancel_text
     - The text of the cancel button
     - No. Defaults to "Cancel".
   * - on_cancel
     - The action to take when the user cancels the dialog. Either "exit" (will end the stream) or "continue".
     - No. Defaults to "exit".

**Form fields**

Take a look at :ref:`formhelper` for an easy way to configure your form fields.


**Output**

This node returns a python dictionary with the form's values.


**Example**

.. code-block:: python

    from atraxiflow.core.stream import *
    from atraxiflow.nodes.gui import *
    from atraxiflow.nodes.common import *
    from atraxiflow.gui.common import *

    ui_form = GUIFormInputNode({
        'window': Window('Create project', 400, 300, False),
        'btn_accept_text': 'Create',
        'text': 'Create a new customer',
        'fields': {
            'firstname': Textfield('First name'),
            'lastname': Textfield('Last name'),
            'company': Combobox('Company', ['ACME Inc.', 'Sunny Day Ltd.']),
            'notes': Textarea('Notes')
        }
    })

    echo_name = EchoOutputNode({'msg': 'Created customer {Text:firstname} {Text:lastname}!'})
    echo_data = EchoOutputNode({'res': 'Text:*'})

    Stream.create() >> ui_form >> echo_name >> echo_data >> flow()


.. image:: /images/form.png