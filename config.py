import logging
import os
import dotenv
import logging.config


dotenv.load_dotenv()


class Config:
    LOG_DIR = os.getenv('LOG_DIR', './logs')
    KAFKA_SERVER = os.getenv('KAFKA_SERVER')
    FLASK_ENV = os.getenv('FLASK_ENV')
    KEYCLOAK_SETTINGS = {
        'server': os.environ['KEYCLOAK_BASE_PATH'],
        'realm': os.environ['KEYCLOAK_REALM'],
        'client_id': os.environ['KEYCLOAK_CLIENT_ID'],
        'client_secret': os.environ['KEYCLOAK_CLIENT_SECRET'],
        'username': os.environ['KEYCLOAK_USERNAME'],
        'password': os.environ['KEYCLOAK_PASSWORD'],
    }
    MONGODB_SETTINGS = {
        'db': os.environ['MONGO_DB'],
        'host': os.environ['MONGO_HOST'],
        'port': os.getenv('MONGO_PORT', '27017'),
        'username': os.environ['MONGO_USER'],
        'password': os.environ['MONGO_PASSWORD'],
        'authentication_source': os.getenv('MONGO_AUTH_SRC', 'admin')
    }
    TEMPLATES = {
        'email_verification': os.environ['TEMPLATE_EMAIL_VERIFICATION'],
        'reset_password': os.environ['TEMPLATE_RESET_PASSWORD']
    }
    URLS = {
        'email_verification': os.environ['URL_EMAIL_VERIFICATION'],
        'owner_email_verification': os.environ['URL_OWNER_EMAIL_VERIFICATION'],
        'reset_password': os.environ['URL_RESET_PASSWORD'],
        'notification_uri': os.environ['NOTIFICATION_URI']
    }


# Set up log
if not os.path.exists(Config.LOG_DIR):
    os.mkdir(Config.LOG_DIR)

if not os.path.isdir(Config.LOG_DIR):
    raise ValueError(f'{Config.LOG_DIR} is not a directory')

logging.config.fileConfig('./logging.ini')
