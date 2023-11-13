from gi.repository import Gtk, Gdk
from datetime import datetime
from gui.objects import App

class DetailsView(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        name_box.append(name_label)
        name_box.append(self.name_entry)
        self.append(name_box)

        sort_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        sort_label = Gtk.Label(label="Sort As", vexpand=False, halign=Gtk.Align.START)
        sort_label.set_css_classes(['entry_title'])
        self.sort_entry = Gtk.Entry(vexpand=False, hexpand=True)
        sort_box.append(sort_label)
        sort_box.append(self.sort_entry)
        self.append(sort_box)

        steam_release_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        steam_release_label = Gtk.Label(label="Steam Release Date", vexpand=False, halign=Gtk.Align.START)
        steam_release_label.set_css_classes(['entry_title'])
        self.steam_release_entry = Gtk.Entry(vexpand=False, hexpand=True)
        self.steam_release_entry.set_editable(False)
        self.steam_release_entry.set_can_focus(False)
        self.steam_release_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "x-office-calendar")
        self.steam_release_entry.connect("icon-press", self.show_calendar_popover)
        steam_release_box.append(steam_release_label)
        steam_release_box.append(self.steam_release_entry)
        self.append(steam_release_box)

        original_release_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)
        original_release_label = Gtk.Label(label="Original Release Date", vexpand=False, halign=Gtk.Align.START)
        original_release_label.set_css_classes(['entry_title'])
        self.original_release_entry = Gtk.Entry(vexpand=False, hexpand=True)
        self.original_release_entry.set_editable(False)
        self.original_release_entry.set_can_focus(False)
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
        self.id_entry.set_text(str(app.id))
        self.name_entry.set_text(app.name)
        self.sort_entry.set_text(app.name)
        self.set_date_from_unix(self.steam_release_entry, 2371269)
        self.set_date_from_unix(self.original_release_entry, 2371269)
