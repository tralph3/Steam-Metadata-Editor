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
from .util import clean_string
from .launch_menu import LaunchMenu

MARGIN = 50

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self._has_loaded_app = False
        self._configure_window()
        self._make_widgets()
        self._configure_widgets()

    def _configure_window(self):
        self.set_default_size(1400, 500)
        self.set_title("Steam Metadata Editor")
        self.set_css_classes(["main_window"])

    def _make_widgets(self):
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._search_entry = Gtk.SearchEntry(placeholder_text="Search by name...")
        scrolled_window = Gtk.ScrolledWindow()
        self._app_column_view = AppColumnView()
        scrolled_frame = Gtk.Frame()
        self._main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            margin_end=MARGIN,
            margin_start=MARGIN,
            margin_top=MARGIN,
            margin_bottom=MARGIN,
            spacing=30,
        )
        details_box = DetailsBox(self.model)
        launch_menu = LaunchMenu(self.model)
        tool_bar = Adw.ToolbarView()
        action_bar = Gtk.ActionBar()
        no_app_status_page = Adw.StatusPage()
        no_app_status_page.set_title("No App Selected")
        no_app_status_page.set_description("Start by selecting an app from the list on the left.")
        no_app_status_page.set_icon_name("dialog-information")

        self._save_button = Gtk.Button(label="Save")
        self._quit_button = Gtk.Button(label="Quit without saving")

        self._save_button.set_css_classes(["button", "main_button"])
        self._quit_button.set_css_classes(["button"])

        scrolled_window.set_child(self._app_column_view)
        scrolled_window.set_hexpand(True)
        scrolled_frame.set_child(scrolled_window)

        left_box.append(self._search_entry)
        left_box.append(scrolled_frame)
        left_box.set_spacing(10)

        self._right_box.append(details_box)
        self._right_box.append(launch_menu)
        self._right_box.set_spacing(30)

        self._main_box.append(left_box)
        self._main_box.append(no_app_status_page)
        self._main_box.set_homogeneous(True)

        action_bar.pack_end(self._save_button)
        action_bar.pack_start(self._quit_button)
        tool_bar.add_bottom_bar(action_bar)
        tool_bar.set_content(self._main_box)
        self.set_child(tool_bar)

    def _configure_widgets(self):
        self._search_entry.connect("search-changed", self._on_search_changed)
        self._app_column_view.add_apps(self._make_app_list())
        self._app_column_view.connect('activate', self._change_current_app)
        self._save_button.connect("clicked", self._save_changes)
        self._quit_button.connect("clicked", lambda *_: self.destroy())

    def _change_current_app(self, column_view, index):
        if not self._has_loaded_app:
            self._has_loaded_app = True
            self._main_box.remove(self._main_box.get_last_child())
            self._main_box.append(self._right_box)
        app: App = column_view.get_model().get_item(index)
        event_emit(Event.SAVE_CHANGES)
        event_emit(Event.LOAD_APP, app)

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
        event_emit(Event.SAVE_CHANGES)
        self.model.write()
