#!/usr/bin/env python3
#
# A Metadata Editor for Steam Applications
# Copyright (C) 2024  Tomás Ralph
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
#
##################################
#                                #
#       Created by tralph3       #
#   https://github.com/tralph3   #
#                                #
##################################

from models.appinfo import AppinfoFile
from models.steam_libraries import SteamLibraries
from view import View
import sys

import json

def main():
    steam_libraries = SteamLibraries("/home/tralph3/.local/share/Steam/")
    model = AppinfoFile("/home/tralph3/.local/share/Steam/appcache/appinfo.vdf", steam_libraries)
    view = View(model, application_id="com.github.Metadata-Editor")
    view.run(sys.argv)

if __name__ == "__main__":
    main()
