from ..decoder import TextVdfDecoder, TextVdfDecodeError
import pytest
import os

TEXT_VDF_MOCK_DIR = os.path.join(os.path.dirname(__file__), "vdf_mocks")


def test_input_sanitization():
    decoder = TextVdfDecoder("\"key\"\n{\n\t\"0\"\t\t\"smth\"\n}\n")
    decoder._sanitize_input()
    assert decoder.contents == "\"key\"{\"0\"\t\t\"smth\"}\n"

def test_decoding():
    with open(f"{TEXT_VDF_MOCK_DIR}/libraryfolders.vdf", "r") as f:
        decoder = TextVdfDecoder(f.read())
    decoded_dict = {
        "libraryfolders": {
            "0": {
                "path": "/some/path",
                "apps": {
                    "this": "test"
                },
                "new": "key",
            },
            "1": {
                "path": "/other/path??",
                "apps": {
                    "42": "007"
                },
            },
        },
    }
    assert decoder.decode() == decoded_dict
