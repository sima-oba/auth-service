from .gunicorn import GunicornApplication
from .server import create_server


def start_flask_server(config, host: str, port: int):
    create_server(config).run(host=host, port=port)


def start_gunicorn_server(config, host: str, port: int, workers: int):
    server = create_server(config)
    options = {'bind': f'{host}:{port}', 'workers': workers, 'timeout': 0}
    GunicornApplication(server, options).run()
