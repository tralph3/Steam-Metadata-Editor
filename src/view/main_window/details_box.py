from gi.repository import Gtk, Gdk
from datetime import datetime
from view.objects import App

class DetailsBox(Gtk.Box):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.currently_loaded_app = None

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(15)
        id_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        id_label = Gtk.Label(label="App ID", vexpand=False, halign=Gtk.Align.START)
        id_label.set_css_classes(['entry_title'])
        self.id_entry = Gtk.Entry(vexpand=False, hexpand=True)
        id_box.append(id_label)
        id_box.append(self.id_entry)
        self.append(id_box)

        name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        name_label = Gtk.Label(label="Name", vexpand=False, halign=Gtk.Align.START)
        name_label.set_css_classes(['entry_title'])
        self.name_entry = Gtk.Entry(vexpand=False, hexpand=True)
        self.name_entry.connect("changed", self._update_app_name)
        name_box.append(name_label)
        name_box.append(self.name_entry)
        self.append(name_box)

        sortas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        sortas_label = Gtk.Label(label="Sort as", vexpand=False, halign=Gtk.Align.START)
        sortas_label.set_css_classes(['entry_title'])
        self.sortas_entry = Gtk.Entry(vexpand=False, hexpand=True)
        self.sortas_entry.set_placeholder_text("Unspecified")
        sortas_box.append(sortas_label)
        sortas_box.append(self.sortas_entry)
        self.append(sortas_box)

        steam_release_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        steam_release_label = Gtk.Label(label="Steam release date", vexpand=False, halign=Gtk.Align.START)
        steam_release_label.set_css_classes(['entry_title'])
        self.steam_release_entry = Gtk.Entry(vexpand=False, hexpand=True)
        self.steam_release_entry.set_editable(False)
        self.steam_release_entry.set_can_focus(False)
        self.steam_release_entry.set_placeholder_text("Unspecified")
        self.steam_release_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "x-office-calendar")
        self.steam_release_entry.connect("icon-press", self.show_calendar_popover)
        steam_release_box.append(steam_release_label)
        steam_release_box.append(self.steam_release_entry)
        self.append(steam_release_box)

        original_release_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        original_release_label = Gtk.Label(label="Original release date", vexpand=False, halign=Gtk.Align.START)
        original_release_label.set_css_classes(['entry_title'])
        self.original_release_entry = Gtk.Entry(vexpand=False, hexpand=True)
        self.original_release_entry.set_editable(False)
        self.original_release_entry.set_can_focus(False)
        self.original_release_entry.set_placeholder_text("Unspecified")
        self.original_release_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "x-office-calendar")
        self.original_release_entry.connect("icon-press", self.show_calendar_popover)
        original_release_box.append(original_release_label)
        original_release_box.append(self.original_release_entry)
        self.append(original_release_box)

    def show_calendar_popover(self, entry, icon_position) -> None:
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
