from gi.repository import Gtk, Gdk
from datetime import datetime
from view.objects import App

class DetailsBox(Gtk.Box):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.currently_loaded_app = None
        self._make_widgets()
        self._connect_signals()

    def _make_widgets(self):
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(15)
        id_box, self.id_entry = self._compose_entry_box("App ID", editable=False)
        name_box, self.name_entry = self._compose_entry_box("Name")
        sortas_box, self.sortas_entry = self._compose_entry_box("Sort as", "Unspecified")
        steam_release_box, self.steam_release_entry = self._compose_entry_box(
            "Steam release date", "Unspecified", False, "x-office-calendar")
        original_release_box, self.original_release_entry = self._compose_entry_box(
            "Original release date", "Unspecified", False, "x-office-calendar")
        self.append(id_box)
        self.append(name_box)
        self.append(sortas_box)
        self.append(steam_release_box)
        self.append(original_release_box)

    @staticmethod
    def _make_label(label: str) -> Gtk.Label:
        label = Gtk.Label(label=label, vexpand=False, halign=Gtk.Align.START)
        label.set_css_classes(['entry_title'])
        return label

    @staticmethod
    def _make_entry(placeholder: str=None, editable: bool=True, icon: str=None) -> Gtk.Entry:
        entry = Gtk.Entry(vexpand=False, hexpand=True)
        if not editable:
            entry.set_editable(False)
            entry.set_can_focus(False)
        if placeholder:
            entry.set_placeholder_text(placeholder)
        if icon:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, icon)
        return entry

    @staticmethod
    def _make_box() -> Gtk.Box:
        return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)

    def _compose_entry_box(self, label: str, placeholder: str=None, editable: bool=True, icon: str=None) -> (Gtk.Box, Gtk.Entry):
        box = self._make_box()
        label = self._make_label(label)
        entry = self._make_entry(placeholder, editable, icon)
        box.append(label)
        box.append(entry)
        return (box, entry)

    def _connect_signals(self):
        self.steam_release_entry.connect("icon-press", self.show_calendar_popover)
        self.original_release_entry.connect("icon-press", self.show_calendar_popover)
        popover = Gtk.Popover()
        popover.set_parent(entry)
        calendar = Gtk.Calendar()
        calendar.connect("day-selected", lambda calendar: self.set_date_from_unix(entry, calendar.get_date().to_unix()))
        popover.set_child(calendar)
        popover.show()

    def set_date_from_unix(self, entry: Gtk.Entry, timestamp: int) -> None:
        date = datetime.fromtimestamp(timestamp)
        formatted_date = date.strftime('%-d of %B, %Y')
        entry.set_text(formatted_date)

    def load_app(self, column_view: Gtk.ColumnView , pos: int) -> None:
        app: App = column_view.get_model().get_item(pos)
        self.currently_loaded_app = app
        appid = app.id
        self.id_entry.set_text(str(app.id))
        self.name_entry.set_text(app.name)
        sortas = self.model.get_app_sortas(appid)
        if sortas:
            self.sortas_entry.set_text(sortas)
        else:
            self.sortas_entry.set_text("")
        steam_release_date = self.model.get_app_steam_release_date(appid)
        if steam_release_date:
            self.set_date_from_unix(self.steam_release_entry, steam_release_date)
        else:
            self.steam_release_entry.set_text("")
        original_release_date = self.model.get_app_original_release_date(appid)
        if original_release_date:
            self.set_date_from_unix(self.original_release_entry, original_release_date)
        else:
            self.original_release_entry.set_text("")

    def _update_app_name(self, _):
        self.model.set_app_name(self.currently_loaded_app.id, self.name_entry.get_text())
