from datetime import datetime
from flask.json import JSONEncoder


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj: any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, set):
            return list(obj)

        return super().default(obj)
