import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Pango
from view.objects import App


class AppColumnView(Gtk.ColumnView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_query = ""

        self.list_store = Gio.ListStore()

        filter_model = Gtk.CustomFilter().new(match_func=self._filter_match)
        self.filter = Gtk.FilterListModel()
        self.filter.set_filter(filter_model)
        self.filter.set_model(self.list_store)

        selection_model = Gtk.SingleSelection().new(model=self.filter)
        self.set_model(selection_model)
        self.set_vexpand(True)
        self.set_hexpand(False)
        self._make_columns()

        self.set_property("single-click-activate", True)

    def add_app(self, app: App):
        self.list_store.append(app)

    def add_apps(self, apps: list[App]):
        for app in apps:
            self.add_app(app)

    def filter_apps_by_name(self, search_term: str):
        self.search_query = clean_string(search_term)
        self.filter.get_filter().changed(Gtk.FilterChange.DIFFERENT)

    def _filter_match(self, app: App):
        return self.search_query in clean_string(app.name)

    def _make_columns(self):
        name_column = Gtk.ColumnViewColumn()
        name_column.set_title("Name")
        name_factory = Gtk.SignalListItemFactory()
        name_factory.connect("setup", self._setup_name_factory)
        name_factory.connect("bind", self._bind_name_factory)
        name_column.set_factory(name_factory)
        name_column.set_expand(True)
        self.append_column(name_column)

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
        column_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.START)
        subtitle_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.START)

        name_label = Gtk.Label()
        name_label.set_halign(Gtk.Align.START)
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        name_label.set_css_classes(['app_title'])

        id_label = Gtk.Label()
        id_label.set_halign(Gtk.Align.START)
        id_label.set_width_chars(10)
        id_label.set_xalign(0)

        type_label = Gtk.Label()
        type_label.set_halign(Gtk.Align.START)
        type_label.set_ellipsize(Pango.EllipsizeMode.END)

        column_container.append(name_label)
        column_container.append(subtitle_container)

        subtitle_container.append(id_label)
        subtitle_container.append(type_label)
        subtitle_container.set_css_classes(['app_subtitle'])

        item.set_child(column_container)

    def _bind_name_factory(self, _fact, item):
        name_label = item.get_child().get_first_child()
        id_label = item.get_child().get_last_child().get_first_child()
        type_label = item.get_child().get_last_child().get_last_child()
        app = item.get_item()
        name_label.set_label(app.name)
        id_label.set_label(str(app.id))
        type_label.set_label(app.type.upper())

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

def clean_string(string: str) -> str:
    return ''.join(char for char in string if char.isalnum()).lower()
