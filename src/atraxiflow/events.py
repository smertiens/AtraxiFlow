#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from typing import Callable, Any

EventID = str

class EventObject:
    def add_listener(self, event: EventID, callable: Callable):
        if event in self._listeners:
            self._listeners[event].append(callable)
        else:
            self._listeners[event] = [callable]

    def remove_listener(self, event: EventID, callable: Callable):
        for ev, callables in self._listeners.items():
            if ev == event:
                for c in callables:
                    if c == callable:
                        self._listeners[ev].remove(c)
                        return

    def fire_event(self, event: EventID, data=Any):
        if event in self._listeners:
            for c in self._listeners[event]:
                c(data)
