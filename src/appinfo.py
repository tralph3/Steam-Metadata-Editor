# A Metadata Editor for Steam Applications
# Copyright (C) 2023  Tomás Ralph
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from struct import pack, unpack
from hashlib import sha1
import os


class IncompatibleVDFError(Exception):
    def __init__(self, vdf_version):
        self.vdf_version = vdf_version


class Appinfo:
    def __init__(self, vdf_path, chooseApps=False, apps=None):
        self.offset = 0

        self.vdf_path = vdf_path

        self.COMPATIBLE_VERSIONS = [0x107564428]

        self.SEPARATOR = b"\x00"
        self.TYPE_DICT = b"\x00"
        self.TYPE_STRING = b"\x01"
        self.TYPE_INT32 = b"\x02"
        self.SECTION_END = b"\x08"

        self.INT_SEPARATOR = int.from_bytes(self.SEPARATOR, "little")
        self.INT_TYPE_DICT = int.from_bytes(self.TYPE_DICT, "little")
        self.INT_TYPE_STRING = int.from_bytes(self.TYPE_STRING, "little")
        self.INT_TYPE_INT32 = int.from_bytes(self.TYPE_INT32, "little")
        self.INT_SECTION_END = int.from_bytes(self.SECTION_END, "little")

        with open(self.vdf_path, "rb") as vdf:
            self.appinfoData = bytearray(vdf.read())

        self.verify_vdf_version()

        # load only the modified apps
        if chooseApps:
            self.parsedAppInfo = {}
            for app in apps:
                self.parsedAppInfo[app] = self.read_app(app)
        else:
            self.parsedAppInfo = self.read_all_apps()

    def read_string(self):
        strEnd = self.appinfoData.find(self.INT_SEPARATOR, self.offset)
        try:
            string = self.appinfoData[self.offset:strEnd].decode("utf-8")
        except UnicodeDecodeError:
            # latin-1 == iso8859-1
            string = self.appinfoData[self.offset:strEnd].decode("latin-1")
            # control character used to determine encoding
            string += "\x06"
        self.offset += strEnd - self.offset + 1
        return string

    def read_int64(self):
        int64 = unpack("<Q", self.appinfoData[self.offset:self.offset + 8])[
            0
        ]
        self.offset += 8
        return int64

    def read_int32(self):
        int32 = unpack("<I", self.appinfoData[self.offset:self.offset + 4])[
            0
        ]
        self.offset += 4
        return int32

    def read_byte(self):
        byte = self.appinfoData[self.offset]
        self.offset += 1
        return byte

    def parse_subsections(self):
        subsection = {}
        value_parsers = {
            self.INT_TYPE_DICT: self.parse_subsections,
            self.INT_TYPE_STRING: self.read_string,
            self.INT_TYPE_INT32: self.read_int32,
        }

        while True:
            value_type = self.read_byte()
            if value_type == self.INT_SECTION_END:
                break

            key = self.read_string()
            value = value_parsers[value_type]()

            subsection[key] = value

        return subsection

    def read_header(self):
        keys = [
            "appid",
            "size",
            "state",
            "last_update",
            "access_token",
            "checksum_text",
            "change_number",
            "checksum_binary",
        ]

        formats = [
            ["<I", 4],
            ["<I", 4],
            ["<I", 4],
            ["<I", 4],
            ["<Q", 8],
            ["<20s", 20],
            ["<I", 4],
            ["<20s", 20],
        ]

        headerData = {}

        for fmt, key in zip(formats, keys):
            value = unpack(
                fmt[0], self.appinfoData[self.offset:self.offset + fmt[1]]
            )[0]
            self.offset += fmt[1]
            headerData[key] = value

        return headerData

    def verify_vdf_version(self):
        version = self.read_int64()
        if version not in self.COMPATIBLE_VERSIONS:
            raise IncompatibleVDFError(version)

    def read_app(self, appID):
        # all relevant apps will have a previous section ending before them
        # this ensures we are indeed getting an appid instead of some other
        # random number
        byteData = self.SECTION_END + pack("<I", appID)
        self.offset = self.appinfoData.find(byteData) + 1
        if self.offset == 0:
            print(f"App {appID} not found")
            os._exit(2)
        app = self.read_header()
        app["sections"] = self.parse_subsections()
        app["installed"] = False
        app["install_path"] = "."
        return app

    def read_all_apps(self):
        apps = {}
        # the last appid is 0 but there's no actual data for it,
        # we skip it by checking 4 less bytes to not get into
        # another loop that would raise exceptions
        while self.offset < len(self.appinfoData) - 4:
            app = self.read_header()
            app["sections"] = self.parse_subsections()
            app["installed"] = False
            app["install_path"] = "."
            apps[app["appid"]] = app
        return apps

    def encode_header(self, data):
        return pack(
            "<4IQ20sI20s",
            data["appid"],
            data["size"],
            data["state"],
            data["last_update"],
            data["access_token"],
            data["checksum_text"],
            data["change_number"],
            data["checksum_binary"],
        )

    def encode_string(self, string):
        if "\x06" in string:
            return string[:-1].encode("latin-1") + self.SEPARATOR
        else:
            return string.encode() + self.SEPARATOR

    def encode_int(self, integer):
        return pack("<I", integer)

    def encode_subsections(self, data):
        encodedData = bytearray()

        for key, value in data.items():

            if type(value) == dict:
                encodedData += (
                    self.TYPE_DICT
                    + self.encode_string(key)
                    + self.encode_subsections(value)
                )
            elif type(value) == str:
                encodedData += (
                    self.TYPE_STRING
                    + self.encode_string(key)
                    + self.encode_string(value)
                )
            elif type(value) == int:
                encodedData += (
                    self.TYPE_INT32
                    + self.encode_string(key)
                    + self.encode_int(value)
                )

        # if it got to this point, this particular dictionary ended
        encodedData += self.SECTION_END
        return encodedData

    def get_text_checksum(self, data):
        formatted_data = self.format_data(data)
        hsh = sha1(formatted_data)
        return hsh.digest()

    def get_binary_checksum(self, data):
        hsh = sha1(data)
        return hsh.digest()

    def update_size_and_checksum(
        self, header, size, checksum_text, checksum_binary
    ):
        header = bytearray(header)
        header[4:8] = pack("<I", size)
        header[24:44] = pack("<20s", checksum_text)
        header[48:68] = pack("<20s", checksum_binary)

        return header

    def update_app(self, appinfo):
        # encode new data
        header = self.encode_header(appinfo)
        sections = self.encode_subsections(appinfo["sections"])
        checksum_text = self.get_text_checksum(appinfo["sections"])
        # appid and size don't count, so we skip them
        # by removing 8 bytes from the header
        size = len(sections) + len(header) - 8

        # find where the app is in the file
        # based on the unmodified header
        appLocation = self.appinfoData.find(header)
        if appLocation == -1:
            appID = pack("<I", appinfo["appid"])
            appLocation = self.appinfoData.find(self.SECTION_END + appID)

        # use the stored size to determine the end of the app
        appEndLocation = appLocation + appinfo["size"] + 8
        checksum_binary = self.get_binary_checksum(sections)

        header = self.update_size_and_checksum(
            header, size, checksum_text, checksum_binary
        )

        # replace the current app data with the new one
        if appLocation != -1:
            self.appinfoData[appLocation:appEndLocation] = header + sections
        else:
            self.appinfoData.extend(header + sections)

    def write_data(self):
        with open(self.vdf_path, "wb") as vdf:
            vdf.write(self.appinfoData)

    def format_data(self, data, numberOfTabs=0):
        """
        Formats a python dictionary into the vdf text format.
        """

        formatted_data = b""
        # set a string with a fixed number of tabs for this instance
        tabs = b"\t" * numberOfTabs

        # re-encode strings with their original encoding
        for key in data.keys():
            if type(data[key]) == dict:
                numberOfTabs += 1

                formatted_data += (
                    tabs
                    + b'"'
                    + key.replace("\\", "\\\\").encode()
                    + b'"'
                    + b"\n"
                    + tabs
                    + b"{"
                    + b"\n"
                    + self.format_data(data[key], numberOfTabs)
                    + tabs
                    + b"}\n"
                )

                numberOfTabs -= 1
            else:
                # \x06 character means the string was decoded with iso8859-1
                # the character gets removed when encoding
                if type(data[key]) == str and "\x06" in data[key]:
                    formatted_data += (
                        tabs
                        + b'"'
                        + key.replace("\\", "\\\\").encode()
                        + b'"'
                        + b"\t\t"
                        + b'"'
                        + data[key][:-1]
                        .replace("\\", "\\\\")
                        .encode("latin-1")
                        + b'"'
                        + b"\n"
                    )
                else:
                    formatted_data += (
                        tabs
                        + b'"'
                        + key.replace("\\", "\\\\").encode()
                        + b'"'
                        + b"\t\t"
                        + b'"'
                        + str(data[key]).replace("\\", "\\\\").encode()
                        + b'"'
                        + b"\n"
                    )

        return formatted_data
