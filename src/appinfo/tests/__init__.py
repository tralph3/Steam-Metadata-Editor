import os

APPINFO_MOCK_DIR = os.path.join(os.path.dirname(__file__), "appinfo_mocks")

TEST_APP_HEADER = {
    "appid"           : 0x6969,
    "size"            : 0x52,
    "state"           : 0x1,
    "last_update"     : 0x153,
    "access_token"    : 0x23,
    "checksum_text"   : b"lT\xccD\xdd6\xc4\x0f '7_m\x99\x02\xcaYRV\xdf",
    "change_number"   : 0x64,
    "checksum_binary" : b'O\x9e\x8aI\x9aD\xcf\x12\x140{\xb4\xef\xb9\xb5c{\x97x\x94',
}

TEST_APP_CONTENT = {
    "appinfo": {
        "appid": 0x6969
    }
}
