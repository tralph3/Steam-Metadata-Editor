from .decoder import AppinfoDecoder, AppinfoDecodeError
from .encoder import AppinfoEncoder

__version__ = '0.1'
__all__ = [
    'dump', 'dumps', 'load', 'loads',
    'AppinfoDecoder', 'AppinfoDecodeError', 'AppinfoEncoder',
]

__author__ = 'Tomás Ralph <tomasralph2000@gmail.com>'


def dump(obj: dict, fp) -> None:
    fp.write(dumps(obj))

def dumps(obj: dict) -> bytearray:
    return AppinfoEncoder(obj).encode()

def load(fp) -> dict:
    return AppinfoDecoder(fp.read()).decode()

def loads(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        return load(f)
