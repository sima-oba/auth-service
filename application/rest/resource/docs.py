import os
from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint


def register(app: Flask, url_prefix):
    swagger_schema = url_prefix + '/doc.json'
    swagger_ui = url_prefix + '/doc'

    @app.get(swagger_schema)
    def get_schema():
        return send_from_directory(
            os.path.dirname(app.instance_path), 'static/doc.json'
        )

    bp = get_swaggerui_blueprint(swagger_ui, swagger_schema)
    app.register_blueprint(bp)
