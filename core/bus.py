from blinker import Namespace

class EventBus:
    def __init__(self):
        self._namespace = Namespace()

    def subscribe(self, channel):
        """Uso como decorador: @bus.subscribe('canal')"""
        def wrapper(func):
            self.connect(channel, func)
            return func
        return wrapper

    def connect(self, channel, callback):
        """Uso manual: bus.connect('canal', callback)"""
        signal = self._namespace.signal(channel)
        signal.connect(callback)

    def publish(self, channel, sender, **payload):
        signal = self._namespace.signal(channel)
        signal.send(sender, **payload)

