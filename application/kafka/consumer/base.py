import logging

from abc import ABC, abstractmethod
from threading import Thread
from confluent_kafka import Consumer, KafkaError, KafkaException


_log = logging.getLogger(__name__)


class BaseConsumer(ABC):
    def __init__(self):
        self._running = False
        self._thread = None

    def _handle_error(self, msg):
        if msg.error().code() == KafkaError._PARTITION_EOF:
            _log.warn(
                f'{msg.topic()}:{msg.partition()}'
                f'reached end at offset {msg.offset()}'
            )
        elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
            _log.warn(msg.error())
        else:
            raise KafkaException(msg.error())

    def _loop(self, config, topic, timeout, asyn):
        consumer = Consumer(config)
        consumer.subscribe([topic])
        _log.info(f'Topic {topic} started')

        try:
            while self._running:
                msg = consumer.poll(timeout=timeout)

                if msg is None:
                    continue

                if msg.error():
                    self._handle_error(msg)
                else:
                    self.process(msg)
                    consumer.commit(asynchronous=asyn)
        except Exception as e:
            _log.exception(e)
        finally:
            self._running = False
            consumer.close()
            _log.info(f'Topic {topic} finished')

    def start(self, config: dict, topic: str, timeout=1.0, asyn=False):
        if self._running:
            _log.warning('Consumer is already running')
            return

        if topic is None:
            raise ValueError('"topic" must not be None')

        if len(topic) == 0 or topic.isspace():
            raise ValueError('"topic" must not be a blank string')

        self._running = True
        args = (config, topic, timeout, asyn)
        self._thread = Thread(target=self._loop, args=args)
        self._thread.daemon = True
        self._thread.start()

    def wait(self):
        if self._thread and self._thread.is_alive():
            self._thread.join()

    def shutdown(self):
        self._running = False
        self.wait()

    @abstractmethod
    def process(self, message: any):
        pass
