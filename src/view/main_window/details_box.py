from gi.repository import Gtk, Gdk
from datetime import datetime
from view.objects import App
from view.events import Event, event_connect
from .util import compose_entry_box

DATE_FORMAT = '%-d of %B, %Y'

class DetailsBox(Gtk.Box):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self._current_app: App = None
        self._new_steam_release_date: int = None
        self._new_original_release_date: int = None
        self._intial_app_values: dict = {
            "name": None,
            "sortas": None,
            "steam_release": None,
            "original_release": None,
        }
        self._make_widgets()
        self._connect_signals()

    def _make_widgets(self):
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(15)
        id_box, self.id_entry = compose_entry_box("App ID", editable=False)
        name_box, self.name_entry = compose_entry_box("Name")
        sortas_box, self.sortas_entry = compose_entry_box("Sort as", "Unspecified")
        steam_release_box, self.steam_release_entry = compose_entry_box(
            "Steam release date", "Unspecified", False, "x-office-calendar")
        original_release_box, self.original_release_entry = compose_entry_box(
            "Original release date", "Unspecified", False, "x-office-calendar")
        self.append(id_box)
        self.append(name_box)
        self.append(sortas_box)
        self.append(steam_release_box)
        self.append(original_release_box)

    def _connect_signals(self):
        self.steam_release_entry.connect("icon-press", self._show_calendar_popover)
        self.original_release_entry.connect("icon-press", self._show_calendar_popover)
        event_connect(Event.LOAD_APP, self.load_app)
        event_connect(Event.SAVE_CHANGES, self._save_current_app)

    def _show_calendar_popover(self, entry, icon_position):
        popover = Gtk.Popover()
        calendar = Gtk.Calendar()
        timestamp = None
        if entry == self.steam_release_entry:
            timestamp = self._intial_app_values["steam_release"]
        elif entry == self.original_release_entry:
            timestamp = self._intial_app_values["original_release"]
        if timestamp:
            timestamp = datetime.fromtimestamp(timestamp)
            calendar.set_year(timestamp.year)
            calendar.set_month(timestamp.month - 1)
            calendar.set_day(timestamp.day)
        popover.set_parent(entry)
        calendar.connect("day-selected", lambda calendar: self._set_date_from_unix(entry, calendar.get_date().to_unix()))
        popover.set_child(calendar)
        popover.set_position(icon_position)
        popover.show()

    def _save_current_app(self):
        self._update_app_name()
        self._update_app_sortas()
        self._update_app_steam_release_date()
        self._update_app_original_release_date()

    def _set_current_app(self, app: App):
        self._current_app = app
        self._intial_app_values = {
            "name": self._current_app.name,
            "sortas": self.model.get_app_sortas(self._current_app.id) or "",
            "steam_release": self.model.get_app_steam_release_date(self._current_app.id),
            "original_release": self.model.get_app_original_release_date(self._current_app.id)
        }
        self._new_steam_release_date = None
        self._new_original_release_date = None

    def _set_entries_by_current_app(self):
        self.id_entry.set_text(str(self._current_app.id))
        self.name_entry.set_text(self._intial_app_values["name"])
        self.sortas_entry.set_text(self._intial_app_values["sortas"])
        self._set_date_from_unix(self.steam_release_entry, self._intial_app_values["steam_release"])
        self._set_date_from_unix(self.original_release_entry, self._intial_app_values["original_release"])

    def _set_date_from_unix(self, entry: Gtk.Entry, timestamp: int):
        if not timestamp:
            entry.set_text("")
            return
        date = datetime.fromtimestamp(timestamp)
        formatted_date = date.strftime('%-d of %B, %Y')
        entry.set_text(formatted_date)
        if entry == self.steam_release_entry:
            self._new_steam_release_date = timestamp
        elif entry == self.original_release_entry:
            self._new_original_release_date = timestamp

    def load_app(self, app: App):
        self._set_current_app(app)
        self._set_entries_by_current_app()

    def _update_app_name(self, _=None):
        name_text = self.name_entry.get_text()
        if name_text != "" and name_text != self._intial_app_values["name"]:
            self.model.set_app_name(self._current_app.id, name_text)

    def _update_app_sortas(self, _=None):
        sortas_text = self.sortas_entry.get_text()
        if sortas_text != "" and sortas_text != self._intial_app_values["sortas"]:
            self.model.set_app_sortas(self._current_app.id, sortas_text)

    def _update_app_steam_release_date(self, _=None):
        if self._new_steam_release_date == self._intial_app_values["steam_release"]:
            return
        self.model.set_app_steam_release_date(self._current_app.id, self._new_steam_release_date)

    def _update_app_original_release_date(self, _=None):
        if self._new_original_release_date == self._intial_app_values["original_release"]:
            return
        self.model.set_app_original_release_date(self._current_app.id, self._new_original_release_date)
