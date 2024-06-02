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
from view.events import Event, event_emit

MARGIN = 50

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self._configure_window()
        self._make_widgets()
        self._configure_widgets()

    def _configure_window(self):
        self.set_default_size(1400, 500)
        self.set_title("Steam Metadata Editor")

    def _make_widgets(self):
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._search_entry = Gtk.SearchEntry(placeholder_text="Search by name...")
        scrolled_window = Gtk.ScrolledWindow()
        self._app_column_view = AppColumnView()
        scrolled_frame = Gtk.Frame()
        main_frame = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            margin_end=MARGIN,
            margin_start=MARGIN,
            margin_top=MARGIN,
            margin_bottom=MARGIN,
            spacing=30,
        )
        details_box = DetailsBox(self.model)
        tool_bar = Adw.ToolbarView()
        action_bar = Gtk.ActionBar()
        self._save_button = Gtk.Button(label="Save")
        self._exit_button = Gtk.Button(label="Exit")

        scrolled_window.set_child(self._app_column_view)
        scrolled_window.set_hexpand(True)
        scrolled_frame.set_child(scrolled_window)

        left_box.append(self._search_entry)
        left_box.append(scrolled_frame)
        left_box.set_spacing(10)

        main_frame.append(left_box)
        main_frame.append(details_box)

        action_bar.pack_end(self._save_button)
        action_bar.pack_start(self._exit_button)
        tool_bar.add_bottom_bar(action_bar)
        tool_bar.set_content(main_frame)
        self.set_child(tool_bar)

    def _configure_widgets(self):
        self._search_entry.connect("search-changed", self._on_search_changed)
        self._app_column_view.add_apps(self._make_app_list())
        self._app_column_view.connect('activate', lambda c, i: event_emit(Event.LOAD_APP, c.get_model().get_item(i)))
        self._save_button.connect("clicked", self._save_changes)
        self._exit_button.connect("clicked", lambda *_: self.destroy())

    def _make_app_list(self) -> [App]:
        app_list = []
        for appid in self.model.get_all_apps():
            name = self.model.get_app_name(appid)
            if name == None: continue
            type = self.model.get_app_type(appid)
            installed = False
            modified = False
            app_list.append(App(
                name or "",
                appid or -1,
                type or "",
                installed,
                modified))
        app_list.sort(key=lambda app: clean_string(app.name))
        return app_list

    def _on_search_changed(self, entry: Gtk.SearchEntry):
        search_query = entry.get_text()
        self._app_column_view.filter_apps_by_name(search_query)

    def _save_changes(self, _=None):
        self.model.write()

def clean_string(string: str) -> str:
    return ''.join(char for char in string if char.isalnum()).lower()
