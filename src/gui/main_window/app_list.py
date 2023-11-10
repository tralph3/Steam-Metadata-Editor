import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Pango
from gui.objects import App
from utils import clean_string


class AppColumnView(Gtk.ColumnView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.search_query = ""

        self.list_store = Gio.ListStore()

        filter_model = Gtk.CustomFilter().new(match_func=self.filter_match)
        self.filter = Gtk.FilterListModel()
        self.filter.set_filter(filter_model)
        self.filter.set_model(self.list_store)

        selection_model = Gtk.SingleSelection().new(model=self.filter)
        self.set_model(selection_model)
        self.set_vexpand(True)
        self.set_hexpand(True)
        self._create_columns()

    def filter_apps_by_name(self, search_term: str) -> None:
        self.search_query = clean_string(search_term)
        self.filter.get_filter().changed(Gtk.FilterChange.DIFFERENT)

    def filter_match(self, app: App) -> None:
        return self.search_query in clean_string(app.name)

    def _create_columns(self) -> None:
        name_column = Gtk.ColumnViewColumn()
        name_column.set_title("Name")
        name_factory = Gtk.SignalListItemFactory()
        name_factory.connect("setup", self._setup_name_factory)
        name_factory.connect("bind", self._bind_name_factory)
        name_column.set_factory(name_factory)
        name_column.set_resizable(True)
        name_column.set_fixed_width(400)
        self.append_column(name_column)

        id_column = Gtk.ColumnViewColumn()
        id_column.set_title("ID")
        id_factory = Gtk.SignalListItemFactory()
        id_factory.connect("setup", self._setup_id_factory)
        id_factory.connect("bind", self._bind_id_factory)
        id_column.set_factory(id_factory)
        id_column.set_fixed_width(80)
        id_column.set_resizable(True)
        self.append_column(id_column)

        type_column = Gtk.ColumnViewColumn()
        type_column.set_title("Type")
        type_factory = Gtk.SignalListItemFactory()
        type_factory.connect("setup", self._setup_type_factory)
        type_factory.connect("bind", self._bind_type_factory)
        type_column.set_factory(type_factory)
        type_column.set_fixed_width(80)
        self.append_column(type_column)

        installed_column = Gtk.ColumnViewColumn()
        installed_column.set_title("Installed")
        installed_factory = Gtk.SignalListItemFactory()
        installed_factory.connect("setup", self._setup_installed_factory)
        installed_factory.connect("bind", self._bind_installed_factory)
        installed_column.set_factory(installed_factory)
        self.append_column(installed_column)

        modified_column = Gtk.ColumnViewColumn()
        modified_column.set_title("Modified")
        modified_factory = Gtk.SignalListItemFactory()
        modified_factory.connect("setup", self._setup_modified_factory)
        modified_factory.connect("bind", self._bind_modified_factory)
        modified_column.set_factory(modified_factory)
        self.append_column(modified_column)

    def _setup_name_factory(self, _fact, item):
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        item.set_child(label)

    def _bind_name_factory(self, _fact, item):
        label = item.get_child()
        app = item.get_item()
        label.set_label(app.name)

    def _setup_id_factory(self, _fact, item):
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        item.set_child(label)

    def _bind_id_factory(self, _fact, item):
        label = item.get_child()
        app = item.get_item()
        label.set_label(str(app.id))

    def _setup_type_factory(self, _fact, item):
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        item.set_child(label)

    def _bind_type_factory(self, _fact, item):
        label = item.get_child()
        app = item.get_item()
        label.set_label(app.type)

    def _setup_installed_factory(self, _fact, item):
        checkbutton = Gtk.CheckButton()
        checkbutton.set_sensitive(False)
        item.set_child(checkbutton)

    def _bind_installed_factory(self, _fact, item):
        checkbutton = item.get_child()
        app = item.get_item()
        checkbutton.set_active(app.installed)

    def _setup_modified_factory(self, _fact, item):
        checkbutton = Gtk.CheckButton()
        checkbutton.set_sensitive(False)
        item.set_child(checkbutton)

    def _bind_modified_factory(self, _fact, item):
        checkbutton = item.get_child()
        app = item.get_item()
        checkbutton.set_active(app.modified)

    def add_app(self, app: App) -> None:
        self.list_store.append(app)

    def add_apps(self, apps: list[App]) -> None:
        for app in apps:
            self.add_app(app)
