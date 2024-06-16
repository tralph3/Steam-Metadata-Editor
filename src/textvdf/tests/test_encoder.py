from .. import TextVdfEncoder, TextVdfDecoder
from .common import decoded_dict, TEXT_VDF_MOCK_DIR
import pytest


def test_encoder():
    with open(f"{TEXT_VDF_MOCK_DIR}/libraryfolders.vdf", "r") as f:
        assert f.read() == TextVdfEncoder(decoded_dict).encode()
