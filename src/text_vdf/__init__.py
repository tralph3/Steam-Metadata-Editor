from .decoder import TextVdfDecoder, TextVdfDecodeError
from .encoder import TextVdfEncoder

__version__ = '0.1'
__all__ = [
    'dump', 'dumps', 'load', 'loads',
    'TextVdfDecoder', 'TextVdfDecodeError', 'TextVdfEncoder',
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
