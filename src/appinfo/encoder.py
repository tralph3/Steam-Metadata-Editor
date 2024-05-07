import struct
from hashlib import sha1
from .header import (HEADER_FORMAT,
                     HEADER_SIZE,
                     SEPARATOR,
                     TYPE_DICT,
                     TYPE_STRING,
                     TYPE_INT32,
                     TYPE_INT64,
                     SECTION_END,
                     LAST_APPID,
                     COMPATIBLE_MAGIC_NUMBERS,
                     COMPATIBLE_UNIVERSES)

class AppinfoEncoder:
    def __init__(self, obj: dict=None):
        self.obj = obj

    def encode(self) -> bytearray:
        result = bytearray()
        result += self._encode_int32(COMPATIBLE_MAGIC_NUMBERS[0])
        result += self._encode_int32(COMPATIBLE_UNIVERSES[0])
        result += self._encode_all_apps(self.obj["apps"])
        result += self._encode_int32(LAST_APPID)
        return result

    def _encode_int32(self, integer: int) -> bytearray:
        return struct.pack("<I", integer)

    def _encode_int64(self, integer: int) -> bytearray:
        return struct.pack("<Q", integer)

    def _encode_string(self, string: str) -> bytearray:
        return string.encode() + SEPARATOR

    def _encode_header(self, header: dict) -> bytearray:
        return struct.pack(HEADER_FORMAT,
                    header["appid"],
                    header["size"],
                    header["state"],
                    header["last_update"],
                    header["access_token"],
                    header["checksum_text"],
                    header["change_number"],
                    header["checksum_binary"])

    def _encode_app_content(self, app_content: dict) -> bytearray:
        encoded_content = bytearray()
        for key, value in app_content.items():
            if isinstance(value, str):
                encoded_content += (
                    TYPE_STRING
                    + self._encode_string(key)
                    + self._encode_string(value))
            elif isinstance(value, int):
                encoded_content += (
                    TYPE_INT32
                    + self._encode_string(key)
                    + self._encode_int32(value))
            elif isinstance(value, dict):
                encoded_content += (
                    TYPE_DICT
                    + self._encode_string(key)
                    + self._encode_app_content(value))
        encoded_content += SECTION_END
        return encoded_content

    def _encode_app(self, app: dict) -> bytearray:
        result = bytearray()
        encoded_content = self._encode_app_content(app["content"])
        self._update_app_header(app, encoded_content)
        result += self._encode_header(app["header"])
        result += encoded_content
        return result

    def _encode_all_apps(self, apps: dict) -> bytearray:
        result = bytearray()
        for app in apps.values():
            result += self._encode_app(app)
        return result

    def _update_app_header(self, app: dict, encoded_content: bytearray):
        # 8 is the number of bytes the appid and size sections take,
        # which are not taken into account for the size calculation
        app["header"]["size"] = len(encoded_content) + HEADER_SIZE - 8
        app["header"]["checksum_text"] = self._get_checksum_text(app["content"])
        app["header"]["checksum_binary"] = self._get_checksum_binary(encoded_content)

    def _get_checksum_text(self, app_contents: dict) -> bytes:
        text_vdf = dict_to_vdf(app_contents)
        hash = sha1(text_vdf)
        return hash.digest()

    def _get_checksum_binary(self, encoded_app: bytearray) -> bytes:
        hash = sha1(encoded_app)
        return hash.digest()


def dict_to_vdf(vdf_dict: dict, indent=0) -> bytearray:
    result = bytearray()
    tabs = b"\t" * indent
    for key in vdf_dict.keys():
        if isinstance(vdf_dict[key], dict):
            indent += 1
            result += (tabs
                + b'"'
                + key.replace("\\", "\\\\").encode()
                + b'"\n'
                + tabs
                + b"{\n"
                + dict_to_vdf(vdf_dict[key], indent)
                + tabs
                + b"}\n")
            indent -= 1
        else:
            result += (tabs
                + b'"'
                + key.replace("\\", "\\\\").encode()
                + b'"'
                + b"\t\t"
                + b'"'
                + str(vdf_dict[key]).replace("\\", "\\\\").encode()
                + b'"\n')
    return result
