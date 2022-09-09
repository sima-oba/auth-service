import click

from config import Config
from application import rest, kafka


@click.group(invoke_without_command=True)
@click.pass_context
def entrypoint(ctx):
    if ctx.invoked_subcommand is None:
        ctx.forward(start_flask_server)


@click.command()
@click.option('--host', default='0.0.0.0', type=click.STRING)  # nosec
@click.option('--port', default=5000, type=click.INT)
def start_flask_server(host: str, port: int):
    rest.start_flask_server(Config, host, port)


@click.command()
@click.option('--host', default='0.0.0.0', type=click.STRING)  # nosec
@click.option('--port', default=5000, type=click.INT)
@click.option('--workers', default=4, type=click.INT)
def start_gunicorn_server(host: str, port: int, workers: int):
    rest.start_gunicorn_server(Config, host, port, workers)


@click.command()
def start_kafka_consumer():
    kafka.start_consumer(Config)


entrypoint.add_command(start_flask_server)
entrypoint.add_command(start_gunicorn_server)
entrypoint.add_command(start_kafka_consumer)


if __name__ == '__main__':
    entrypoint()
