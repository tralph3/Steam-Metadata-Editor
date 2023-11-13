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
from gi.repository import Gtk, Adw
from .app_list import AppColumnView
from appinfo import Appinfo
from gui.objects import App
from utils import clean_string
from .details_view import DetailsView

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(1400, 500)
        self.set_title("Steam-Metadata-Editor")

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search_entry = Gtk.SearchEntry(placeholder_text="Search by name...")
        search_entry.connect("search-changed", self.on_search_changed)
        appinfo = Appinfo()
        appinfo.load("/home/tralph3/.local/share/Steam/appcache/appinfo.vdf")
        app_list = []
        for app in appinfo.parsedAppInfo.keys():
            id = app
            try:
                name = appinfo.parsedAppInfo[id]["sections"]["appinfo"]["common"]["name"]
            except KeyError:
                continue
            type = appinfo.parsedAppInfo[id]["sections"]["appinfo"]["common"]["type"]
            installed = False
            modified = False
            app_list.append(App(name, id, type, installed, modified))
        self.app_column_view = AppColumnView()
        app_list.sort(key=lambda app: clean_string(app.name))
        self.app_column_view.add_apps(app_list)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.app_column_view)
        scrolled_window.set_hexpand(True)
        scrolled_frame = Gtk.Frame()
        scrolled_frame.set_child(scrolled_window)
        left_box.append(search_entry)
        left_box.append(scrolled_frame)
        left_box.set_spacing(10)
        MARGIN = 50
        main_frame = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            margin_end=MARGIN,
            margin_start=MARGIN,
            margin_top=MARGIN,
            margin_bottom=MARGIN,
            spacing=30,
        )
        main_frame.append(left_box)
        details_view = DetailsView()
        main_frame.append(details_view)
        self.app_column_view.connect('activate', details_view.load_app)
        self.set_child(main_frame)

    def on_search_changed(self, entry: Gtk.SearchEntry):
        search_query = entry.get_text()
        self.app_column_view.filter_apps_by_name(search_query)
