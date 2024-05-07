import struct

COMPATIBLE_MAGIC_NUMBERS = [ 0x07564428 ]
COMPATIBLE_UNIVERSES     = [ 0x01 ]

HEADER_FORMAT = "<4IQ20sI20s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

LAST_APPID = 0x00

SEPARATOR = b"\x00"
TYPE_DICT = b"\x00"
TYPE_STRING = b"\x01"
TYPE_INT32 = b"\x02"
TYPE_INT64 = b"\x07"
SECTION_END = b"\x08"

INT_SEPARATOR = int.from_bytes(SEPARATOR, "little")
INT_TYPE_DICT = int.from_bytes(TYPE_DICT, "little")
INT_TYPE_STRING = int.from_bytes(TYPE_STRING, "little")
INT_TYPE_INT32 = int.from_bytes(TYPE_INT32, "little")
INT_TYPE_INT64 = int.from_bytes(TYPE_INT64, "little")
INT_SECTION_END = int.from_bytes(SECTION_END, "little")
