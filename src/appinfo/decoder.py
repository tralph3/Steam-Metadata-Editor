import struct
from .header import (HEADER_FORMAT,
                     HEADER_SIZE,
                     INT_SEPARATOR,
                     INT_TYPE_DICT,
                     INT_TYPE_STRING,
                     INT_TYPE_INT32,
                     INT_TYPE_INT64,
                     INT_SECTION_END,
                     LAST_APPID,
                     COMPATIBLE_MAGIC_NUMBERS,
                     COMPATIBLE_UNIVERSES)


class AppinfoDecodeError(Exception):
    pass


class AppinfoDecoder:
    def __init__(self, contents: bytearray):
        self.contents = contents
        self.pointer = 0
        self._decoders = {
            INT_TYPE_DICT: self._read_app_content,
            INT_TYPE_STRING: self._read_string,
            INT_TYPE_INT32: self._read_int32,
            INT_TYPE_INT64: self._read_int64,
        }

    def decode(self) -> dict:
        self._validate_vdf_version()
        return {
            "apps": self._read_all_apps()
        }

    def _is_magic_number_valid(version: int) -> bool:
        return version in COMPATIBLE_MAGIC_NUMBERS

    def _is_universe_valid(universe: int) -> bool:
        return universe in COMPATIBLE_UNIVERSES

    def _validate_vdf_version(self):
        magic = self._read_int32()
        universe = self._read_int32()
        if not AppinfoDecoder._is_magic_number_valid(magic) or \
           not AppinfoDecoder._is_universe_valid(universe):
            raise AppinfoDecodeError(f"Invalid VDF version: Magic: {magic}, Universe: {universe}")

    def _read(self, count: int) -> bytearray:
        result = self.contents[self.pointer:self.pointer + count]
        self.pointer += count
        return result

    def _read_byte(self) -> int:
        return int.from_bytes(self._read(1))

    def _read_int32(self) -> int:
        return struct.unpack("<I", self._read(4))[0]

    def _read_int64(self) -> int:
        return struct.unpack("<Q", self._read(8))[0]

    def _read_string(self) -> bytes:
        str_end = self.contents.find(INT_SEPARATOR, self.pointer)
        string = self._read(str_end - self.pointer)
        self._read_byte()
        return string.decode("utf-8")

    def _peek_appid(self):
        current_pointer = self.pointer
        next_appid = self._read_int32()
        self.pointer = current_pointer
        return next_appid

    def _read_app_header(self) -> dict:
        header_content = struct.unpack(HEADER_FORMAT, self._read(HEADER_SIZE))
        return {
            "appid"           : header_content[0],
            "size"            : header_content[1],
            "state"           : header_content[2],
            "last_update"     : header_content[3],
            "access_token"    : header_content[4],
            "checksum_text"   : header_content[5],
            "change_number"   : header_content[6],
            "checksum_binary" : header_content[7],
        }

    def _read_app_content(self) -> dict:
        content = {}
        while True:
            value_type = self._read_byte()
            if value_type == INT_SECTION_END: break
            key = self._read_string()
            value = self._decoders[value_type]()
            content[key] = value
        return content

    def _read_app(self) -> dict:
        return {
            "header": self._read_app_header(),
            "content": self._read_app_content(),
        }

    def _read_all_apps(self) -> dict:
        apps = {}
        while True:
            appid = self._peek_appid()
            if appid == LAST_APPID: break
            apps[appid] = self._read_app()
        return apps
