
class EventObject:
    def add_listener(self, event, callable):
        if event in self._listeners:
            self._listeners[event].append(callable)
        else:
            self._listeners[event] = [callable]

    def remove_listener(self, event, callable):
        for ev, callables in self._listeners.items():
            if ev == event:
                for c in callables:
                    if c == callable:
                        self._listeners[ev].remove(c)
                        return

    def fire_event(self, event, data = None):
        if event in self._listeners:
            for c in self._listeners[event]:
                c(data)
