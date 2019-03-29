GUI functions
=============

In order to use the gui functions you need to install Pyside2 (`<https://pypi.org/project/PySide2/>`_).

.. _streamui:


Stream UI
---------

If you don't want to rely on the terminal for output, you can use the built in UI by using the :py:class:`GUIStream`
class.

.. code-block:: python

    from atraxiflow.core.stream import *
    from atraxiflow.nodes.gui import *
    from atraxiflow.nodes.common import *
    from atraxiflow.gui.common import *

    st = Stream()
    st.append_node(DelayNode({'time': '2'}))
    ui = GUIStream.from_stream(st)
    ui.flow()

.. image:: /images/ui.png

.. autoclass:: atraxiflow.gui.common.GUIStream
    :members:



.. _formhelper:

Form field helper
-----------------

.. automodule:: atraxiflow.gui.common
    :members: Checkbox, Combobox, Password, Textarea, Textfield


.. _windowhelper:

Window helper
-------------

.. autofunction:: atraxiflow.gui.common.Window