#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import logging
from typing import Callable, Any

__all__ = ['EventObject', 'EventID']

EventID = str


class EventObject:
    """
    Objects can inherit from EventObject to be able to fire/react on events
    To store the connected callbacks, the child class must define the _listeners variable in its constructor:

    .. code-block:: python

        self._listeners = {}

    """

    def add_listener(self, event: EventID, callable: Callable):
        if event in self._listeners:
            self._listeners[event].append(callable)
        else:
            self._listeners[event] = [callable]

        logging.getLogger('core').debug('Added listener for %s' % event)

    def remove_listener(self, event: EventID, callable: Callable):
        for ev, callables in self._listeners.items():
            if ev == event:
                for c in callables:
                    if c == callable:
                        self._listeners[ev].remove(c)
                        return

        logging.getLogger('core').debug('Removed one listener for %s' % event)

    def fire_event(self, event: EventID, data=Any):
        if event in self._listeners:
            for c in self._listeners[event]:
                logging.getLogger('core').debug('Executing listener for %s' % event)
                c(data)
