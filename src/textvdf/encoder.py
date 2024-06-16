import json


class TextVdfEncoder:
    def __init__(self, obj: dict=None):
        self._obj = obj
        self._indent = 0

    def encode(self, obj: dict=None) -> str:
        result = ""
        tabs = "\t" * self._indent
        if obj is None: obj = self._obj
        for key in obj:
            if isinstance(obj[key], dict):
                self._indent += 1
                value = self.encode(obj[key])
                key = key.replace("\\", "\\\\")
                result += f'{tabs}"{key}"\n{tabs}{"{\n"}{value}{tabs}{"}\n"}'
                self._indent -= 1
            else:
                value = str(obj[key]).replace("\\", "\\\\")
                key = key.replace("\\", "\\\\")
                result += f'{tabs}"{key}"\t\t"{value}"\n'
        return result
