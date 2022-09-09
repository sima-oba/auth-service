from domain.service import RegistrationService
from infrastructure.database import get_database
from infrastructure.keycloak import Keycloak
from infrastructure.repository import (
    SecurityRepository,
    TokenRepository,
    Notifier
)
from .consumer import Consumer, ConsumerGroup
from ..schema import OwnerSchema


def start_consumer(config):
    group = ConsumerGroup({
        'bootstrap.servers': config.KAFKA_SERVER,
        'group.id': 'AUTH',
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest'
    })

    db = get_database(config.MONGODB_SETTINGS)
    keycloak = Keycloak(**config.KEYCLOAK_SETTINGS)
    security_repo = SecurityRepository(keycloak)
    token_repo = TokenRepository(db)

    notifier = Notifier({
        'bootstrap.servers': config.KAFKA_SERVER,
        'client.id': 'AUTH',
        'message.max.bytes': 33554432
    }, config.TEMPLATES, config.URLS)

    owner_svc = RegistrationService(notifier, security_repo, token_repo)
    owner_consumer = Consumer(OwnerSchema(), owner_svc.import_owner)
    group.add(owner_consumer, 'NEW_OWNER')
    group.wait()
