from ..decoder import TextVdfDecoder, TextVdfDecodeError
from .common import decoded_dict, TEXT_VDF_MOCK_DIR
import pytest


def test_input_sanitization():
    decoder = TextVdfDecoder("\"key\"\n{\n\t\"0\"\t\t\"smth\"\n}\n")
    decoder._sanitize_input()
    assert decoder.contents == "\"key\"{\"0\"\t\t\"smth\"}\n"

def test_decoding():
    with open(f"{TEXT_VDF_MOCK_DIR}/libraryfolders.vdf", "r") as f:
        assert TextVdfDecoder(f.read()).decode() == decoded_dict
