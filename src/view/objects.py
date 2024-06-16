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
from gi.repository import GObject

class App(GObject.Object):
    name=GObject.Property(type=str, default="")
    id=GObject.Property(type=int, default=-1)
    installed=GObject.Property(type=bool, default=False)
    type=GObject.Property(type=str, default="")
    modified=GObject.Property(type=bool, default=False)

    def __init__(self, name: str, id: int, type: str, installed: bool, modified: bool) -> None:
        super().__init__()
        self.name = name
        self.id = id
        self.type = type
        self.installed = installed
        self.modified = modified
