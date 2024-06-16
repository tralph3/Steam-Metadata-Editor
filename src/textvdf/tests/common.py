import os


TEXT_VDF_MOCK_DIR = os.path.join(os.path.dirname(__file__), "vdf_mocks")

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
