from dataclasses import is_dataclass
import dataclasses
import json
from datetime import date

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return dataclasses.asdict(o)
        if type(o) == date:
            return str(o.strftime("%Y-%m-%d"))
        return super().default(o)