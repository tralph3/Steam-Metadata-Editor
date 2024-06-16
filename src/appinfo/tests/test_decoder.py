from ..decoder import AppinfoDecoder, AppinfoDecodeError
import struct
import pytest
import os
from . import APPINFO_MOCK_DIR, TEST_APP_CONTENT, TEST_APP_HEADER

TEST_VDF_BAD_MAGIC    = 0x6969
TEST_VDF_MAGIC_NUMBER = 0x07564428
TEST_VDF_UNIVERSE     = 0x01


def test_compatible_versions():
    version = struct.pack("<2I", TEST_VDF_MAGIC_NUMBER, TEST_VDF_UNIVERSE)
    # means no error is raised
    assert AppinfoDecoder(version)._validate_vdf_version() == None
    with pytest.raises(AppinfoDecodeError):
        version = struct.pack("<2I", TEST_VDF_BAD_MAGIC, TEST_VDF_UNIVERSE)
        AppinfoDecoder(version)._validate_vdf_version()

def test_read_app_header():
    with open(f"{APPINFO_MOCK_DIR}/app_header.vdf", "rb") as f:
        content = f.read()
        print(content)
        result = AppinfoDecoder(content)._read_app_header()
        print(result["checksum_text"])
        print(TEST_APP_HEADER["checksum_text"])
        assert result == TEST_APP_HEADER

def test_read_app_content():
    with open(f"{APPINFO_MOCK_DIR}/app_content.vdf", "rb") as f:
        app_content = f.read()
        result = AppinfoDecoder(app_content)._read_app_content()
        assert result == TEST_APP_CONTENT

def test_read_app():
    with open(f"{APPINFO_MOCK_DIR}/single_app.vdf", "rb") as f:
        content = f.read()
        result = AppinfoDecoder(content)._read_app()
        assert result["header"] == TEST_APP_HEADER
        assert result["content"] == TEST_APP_CONTENT

def test_read_real_appinfo():
    with open(f"{APPINFO_MOCK_DIR}/real_appinfo_slice.vdf", "rb") as f:
        content = f.read()
        result = AppinfoDecoder(content).decode()
        assert len(result["apps"]) == 4
        assert result["apps"][5]["header"]["appid"] == 5
        assert result["apps"][7]["header"]["appid"] == 7
        assert result["apps"][8]["header"]["appid"] == 8
        assert result["apps"][10]["header"]["appid"] == 10
