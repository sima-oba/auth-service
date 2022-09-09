import json
from confluent_kafka import Producer

from domain.model import Owner
from domain.repository import IProtocolPublisher


class ProtocolPublisher(IProtocolPublisher):
    def __init__(self, config: dict):
        self._producer = Producer(config)

    def send_new_owner(self, owner: Owner):
        payload = json.dumps({
            'requester': 'AUTH-SERVICE',
            'protocol_type': 'NEW_OWNER',
            'priority': 1,
            'owner': owner.asdict()
        }, ensure_ascii=False)

        self._producer.produce('PROTOCOL_NEW_OWNER', payload, owner._id)
        self._producer.flush()
