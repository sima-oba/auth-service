from pymongo import MongoClient
from pymongo.database import Database


def get_database(config: dict) -> Database:
    db = config['db']
    host = config.get('host', 'localhost')
    port = config.get('port', '27017')
    username = config['username']
    password = config['password']
    auth_source = config.get('authentication_source', 'admin')

    params = f'authSource={auth_source}'
    uri = f'mongodb://{username}:{password}@{host}:{port}/?{params}'
    client = MongoClient(uri, tz_aware=True)
    return client[db]
