import logging

from ..model import Group
from ..repository import ISecurityRepository


DEFAULT_ROLES = [
    'manage-notifications',
    'manage-occurrences',
    'read-hydrography',
    'read-notifications',
    'read-ordinances',
    'read-properties',
    'read-protocols',
    'read-risk',
    'read-visits',
    'read-weather',
    'report-occurrences',
    'write-properties',
    'write-protocols'
]

DEFAULT_GROUPS = [
    {
        'group': 'aiba',
        'roles': DEFAULT_ROLES
    },
    {
        'group': 'public',
        'roles': [
            'read-hydrography',
            'read-risk',
            'read-weather'
        ]
    },
    {
        'group': 'producer',
        'roles': [
            'read-hydrography',
            'read-notifications',
            'read-ordinances',
            'read-properties',
            'read-protocols',
            'read-risk',
            'read-visits',
            'read-weather',
            'report-occurrences',
            'write-properties',
            'write-protocols'
        ]
    }
]


class SettingsService:
    def __init__(self, repo: ISecurityRepository):
        self._repo = repo
        self._log = logging.getLogger(self.__class__.__name__)

    def init_settings(self):
        self._log.info('Initialing settings')

        for role in DEFAULT_ROLES:
            self._repo.create_role(role)
            self._log.debug(f'Added role {role}')

        for group in DEFAULT_GROUPS:
            group = Group(None, group['group'], group['roles'])
            self._repo.create_group(group)
            self._log.debug(f'Added group {group.name}')
