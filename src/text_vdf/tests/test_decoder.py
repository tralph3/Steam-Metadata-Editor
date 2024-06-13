from ..decoder import TextVdfDecoder, TextVdfDecodeError
import pytest


def test_input_sanitization():
    decoder = TextVdfDecoder("\"key\"\n{\n\t\"0\"\t\t\"smth\"\n}\n")
    decoder.sanitize_input()
    assert decoder.contents == "\"key\"{\"0\"\t\t\"smth\"}"
