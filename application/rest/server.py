from flask import Flask
from flask_cors import CORS

from domain.service import (
    AuthService,
    AccountService,
    SettingsService,
    RegistrationService
)
from infrastructure.database import get_database
from infrastructure.keycloak import Keycloak
from infrastructure.repository import (
    SecurityRepository,
    TokenRepository,
    Notifier,
    ProtocolPublisher
)
from .resource import (
    docs,
    registration,
    session,
    users,
    groups,
    roles,
    settings
)
from .encoder import CustomJsonEncoder
from .error import error_bp
from .security import Authorization, Role


URL_PREFIX = '/api/v1/auth'


def create_server(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['JSON_SORT_KEYS'] = False
    app.json_encoder = CustomJsonEncoder
    app.register_blueprint(error_bp)

    docs.register(app, URL_PREFIX)
    CORS(app)

    keycloak = Keycloak(**config.KEYCLOAK_SETTINGS)
    security_repo = SecurityRepository(keycloak)
    db = get_database(config.MONGODB_SETTINGS)

    is_auth_enabled = config.FLASK_ENV != 'development'
    auth = Authorization(keycloak.cli_openid, is_auth_enabled)
    auth.grant_role_for_any_request(Role.ADMIN)

    notifier = Notifier({
        'bootstrap.servers': config.KAFKA_SERVER,
        'client.id': 'AUTH',
        'message.max.bytes': 32 * 1024 ** 2
    }, config.TEMPLATES, config.URLS)

    protocol_pub = ProtocolPublisher({
        'bootstrap.servers': config.KAFKA_SERVER,
        'client.id': 'AUTH'
    })

    token_repo = TokenRepository(db)
    account_svc = AccountService(
        security_repo,
        token_repo,
        notifier,
        protocol_pub
    )

    auth_svc = AuthService(security_repo)
    session_bp = session.get_blueprint(auth_svc)
    app.register_blueprint(session_bp, url_prefix=URL_PREFIX)

    users_bp = users.get_blueprint(account_svc, auth)
    app.register_blueprint(users_bp, url_prefix=URL_PREFIX)

    groups_bp = groups.get_blueprint(account_svc)
    auth.require_authorization_for_any_request(groups_bp)
    app.register_blueprint(groups_bp, url_prefix=URL_PREFIX)

    roles_bp = roles.get_blueprint(account_svc)
    auth.require_authorization_for_any_request(roles_bp)
    app.register_blueprint(roles_bp, url_prefix=URL_PREFIX)

    settings_svc = SettingsService(security_repo)
    settings_bp = settings.get_blueprint(settings_svc)
    auth.require_authorization_for_any_request(settings_bp)
    app.register_blueprint(settings_bp, url_prefix=URL_PREFIX)

    owner_reg_svc = RegistrationService(notifier, security_repo, token_repo)
    registration_bp = registration.get_blueprint(owner_reg_svc)
    app.register_blueprint(registration_bp, url_prefix=URL_PREFIX)

    return app
