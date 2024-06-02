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
from gi.repository import Gtk, Adw
from .app_list import AppColumnView
from view.objects import App
from .details_box import DetailsBox

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.set_default_size(1400, 500)
        self.set_title("Steam Metadata Editor")

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search_entry = Gtk.SearchEntry(placeholder_text="Search by name...")
        search_entry.connect("search-changed", self.on_search_changed)
        app_list = []
        for appid in self.model.get_all_apps():
            name = self.model.get_app_name(appid)
            if name == None: continue
            type = self.model.get_app_type(appid)
            installed = False
            modified = False
            app_list.append(App(name, appid, type, installed, modified))

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
        details_box = DetailsBox(self.model)
        main_frame.append(details_box)
        self.app_column_view.connect('activate', details_box.load_app)
        tool_bar = Adw.ToolbarView()
        action_bar = Gtk.ActionBar()
        save_button = Gtk.Button(label="Save")
        exit_button = Gtk.Button(label="Exit")
        save_button.connect("clicked", self._save_changes)
        exit_button.connect("clicked", lambda *_: self.destroy())
        action_bar.pack_end(save_button)
        action_bar.pack_start(exit_button)
        tool_bar.add_bottom_bar(action_bar)
        tool_bar.set_content(main_frame)
        self.set_child(tool_bar)

    def on_search_changed(self, entry: Gtk.SearchEntry):
        search_query = entry.get_text()
        self.app_column_view.filter_apps_by_name(search_query)

    def _save_changes(self, _):
        self.model.write()

def clean_string(string: str) -> str:
    return ''.join(char for char in string if char.isalnum()).lower()
