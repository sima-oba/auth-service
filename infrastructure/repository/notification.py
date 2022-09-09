import json
import logging
import requests
from base64 import urlsafe_b64encode
from datetime import datetime
from confluent_kafka import Producer

from domain.exception import UnexpectedError
from domain.model import User
from domain.repository import INotifier


class Notifier(INotifier):
    def __init__(self, config: dict, templates: dict, urls: dict):
        self._config = config
        self._templates = templates
        self._urls = urls

    def _send(self, template_id, subject, user, link, code):
        code = str(urlsafe_b64encode(code.encode('ascii')), 'utf-8')
        payload = json.dumps({
            'email': {
                'template_id': template_id,
                'subject': subject,
                'recipient': [user.email],
                'content': {
                    'first_name': user.firstName,
                    'link': link + '/' + code
                }
            }
        }, ensure_ascii=False)

        _id = f'{user.id}:{datetime.utcnow().isoformat()}'
        producer = Producer(self._config)
        producer.produce('NOTIFICATION', key=_id, value=payload)
        producer.flush()

    def send_owner_email_verification(self, user: User, code: str):
        self._send(
            self._templates['email_verification'],
            '[SIMA] - Verificação de e-mail',
            user,
            self._urls['owner_email_verification'],
            code
        )

    def send_email_verification(self, user: User, code: str):
        self._send(
            self._templates['email_verification'],
            '[SIMA] - Verificação de e-mail',
            user,
            self._urls['email_verification'],
            code
        )

    def send_reset_password(self, user: User, code: str):
        self._send(
            self._templates['reset_password'],
            '[SIMA] - Redefinição de senha',
            user,
            self._urls['reset_password'],
            code
        )


class HttpNotifier:
    def __init__(self, templates: dict, urls: str):
        self._templates = templates
        self._urls = urls
        self._log = logging.getLogger(self.__class__.__name__)

    def _send(self, template_id, subject, user, link, code):
        code = str(urlsafe_b64encode(code.encode('ascii')), 'utf-8')
        payload = {
            'email': {
                'template_id': template_id,
                'subject': subject,
                'recipient': [user.email],
                'content': {
                    'first_name': user.firstName,
                    'link': link + '/' + code
                }
            }
        }

        response = requests.post(self._urls['notification_uri'], json=payload)

        if not response.ok:
            self._log.error(response.text)
            raise UnexpectedError(response.text)

    def send_owner_email_verification(self, user: User, code: str):
        self._send(
            self._templates['email_verification'],
            '[SIMA] - Verificação de e-mail',
            user,
            self._urls['owner_email_verification'],
            code
        )

    def send_email_verification(self, user: User, code: str):
        self._send(
            self._templates['email_verification'],
            '[SIMA] - Verificação de e-mail',
            user,
            self._urls['email_verification'],
            code
        )

    def send_reset_password(self, user: User, code: str):
        self._send(
            self._templates['reset_password'],
            '[SIMA] - Redefinição de senha',
            user,
            self._urls['reset_password'],
            code
        )
