import json


class TextVdfEncoder:
    def __init__(self, obj: dict=None):
        self.obj = obj

    def encode(self, obj=None, indent=0) -> str:
        result = ""
        tabs = "\t" * indent
        if obj is None:
            obj = self.obj
        for key in obj.keys():
            if isinstance(obj[key], dict):
                indent += 1
                value = self.encode(obj[key], indent)
                key = key.replace("\\", "\\\\")
                result += f'{tabs}"{key}"\n{tabs}{"{\n"}{value}{tabs}{"}\n"}'
                indent -= 1
            else:
                value = str(obj[key]).replace("\\", "\\\\")
                key = key.replace("\\", "\\\\")
                result += f'{tabs}"{key}"\t\t"{value}"\n'
        return result
