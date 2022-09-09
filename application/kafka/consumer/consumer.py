import signal
from typing import Callable, Any
from marshmallow import Schema

from .base import BaseConsumer
from .error import error_handler


class Consumer(BaseConsumer):
    def __init__(self, schema: Schema, callback: Callable[[dict], Any]):
        super().__init__()
        self._schema = schema
        self._callback = callback

    @error_handler
    def process(self, msg: any):
        data = self._schema.loads(msg.value())
        self._callback(data)


class ConsumerGroup:
    def __init__(self, config: dict) -> None:
        self._config = config
        self._consumers = []

    def add(self, consumer: BaseConsumer, topic: str):
        consumer.start(self._config, topic)
        self._consumers.append(consumer)

    def wait(self):
        def shutdown(*_):
            self.shutdown()

        signal.signal(signal.SIGHUP, shutdown)
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        for consumer in self._consumers:
            consumer.wait()

    def shutdown(self):
        for consumer in self._consumers:
            consumer.shutdown()
