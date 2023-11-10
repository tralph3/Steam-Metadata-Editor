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
from gi.repository import Gtk
from .app_list import AppColumnView
from appinfo import Appinfo
from gui.objects import App

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(600, 250)
        self.set_title("Steam-Metadata-Editor")
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(left_box)
        appinfo = Appinfo("/home/tralph3/.local/share/Steam/appcache/appinfo.vdf")
        app_list = []
        for app in list(appinfo.parsedAppInfo.keys())[3:]:
            id = app
            try:
                name = appinfo.parsedAppInfo[id]["sections"]["appinfo"]["common"]["name"]
            except KeyError:
                continue
            type = appinfo.parsedAppInfo[id]["sections"]["appinfo"]["common"]["type"]
            installed = False
            modified = False
            app_list.append(App(name, id, type, installed, modified))
        app_column_view = AppColumnView()
        app_column_view.add_apps(app_list)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(app_column_view)
        scrolled_window.set_hexpand(True)

        left_box.append(scrolled_window)
