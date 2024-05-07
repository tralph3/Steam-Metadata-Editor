from .. import AppinfoEncoder, AppinfoDecoder
from . import APPINFO_MOCK_DIR, TEST_APP_CONTENT, TEST_APP_HEADER


def test_encode_header():
    with open(f"{APPINFO_MOCK_DIR}/app_header.vdf", "rb") as f:
        result = AppinfoEncoder()._encode_header(TEST_APP_HEADER)
        assert result == f.read()

def test_encode_app_content():
    with open(f"{APPINFO_MOCK_DIR}/app_content.vdf", "rb") as f:
        result = AppinfoEncoder()._encode_app_content(TEST_APP_CONTENT)
        assert result == f.read()

def test_encode_app():
    with open(f"{APPINFO_MOCK_DIR}/single_app.vdf", "rb") as f:
        app = {
            "header": TEST_APP_HEADER,
            "content": TEST_APP_CONTENT,
        }
        result = AppinfoEncoder()._encode_app(app)
        assert result == f.read()

def test_encode_real_appinfo():
    with open(f"{APPINFO_MOCK_DIR}/real_appinfo_slice.vdf", "rb") as f:
        contents = f.read()
        decoded = AppinfoDecoder(contents).decode()
        encoded = AppinfoEncoder(decoded).encode()
        assert encoded == contents

def test_header_update():
    expected_size = 0x63
    app = {
        "header": TEST_APP_HEADER,
        "content": {'appinfo': {'appid': 5, 'public_only': 1}},
    }
    result = AppinfoEncoder()._encode_app(app)
    updated_header = AppinfoDecoder(result)._read_app_header()
    assert updated_header["size"] == 0x63
    assert updated_header["checksum_text"] == b'\x87\xfaCg\x85\x80\r\xb4\x90Im\xdc}\xb4\x81\xeeQ\x8b\x825'
    assert updated_header["checksum_binary"] == b'\x85\x1a1#u\xf0E\x9a,\x93\xe2\x8a7\xd1XT\xa1\x82\xb9\x89'
