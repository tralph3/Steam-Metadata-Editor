from gi.repository import Gtk, Gdk
from view.objects import App
from view.events import Event, event_connect
from .util import compose_entry_box, _make_box

class LaunchEntry(Gtk.Box):
    def __init__(self, entry, index: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry = entry
        self.index = index
        self._make_widgets()
        self._configure_widgets()

    def _make_widgets(self):
        self.set_orientation(Gtk.Orientation.VERTICAL)
        desc_box, self.desc_entry = compose_entry_box("Description", "Unspecified")
        exec_box, self.exec_entry = compose_entry_box("Executable", "Unspecified", False, "folder")
        workdir_box, self.workdir_entry = compose_entry_box("Working Directory", "Unspecified", False, "folder")
        args_box, self.args_entry = compose_entry_box("Launch Arguments", "Unspecified")
        self.append(desc_box)
        self.append(exec_box)
        self.append(workdir_box)
        self.append(args_box)

    def _configure_widgets(self):
        css_class = ""
        if self.index % 2 == 0:
            css_class = "launch_entry_even"
        else:
            css_class = "launch_entry_odd"
        self.set_spacing(15)
        self.set_css_classes([css_class])
        self.desc_entry.set_text(self.entry.get("description", ""))
        self.exec_entry.set_text(self.entry.get("executable", ""))
        self.workdir_entry.set_text(self.entry.get("workingdir", ""))
        self.args_entry.set_text(self.entry.get("arguments", ""))


class LaunchMenu(Gtk.Frame):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self._current_app: App = None
        self.set_vexpand(True)
        self._make_widgets()
        self._connect_signals()
        self.set_css_classes(['launch_menu'])

    def _make_widgets(self):
        scrolled_window = Gtk.ScrolledWindow()
        self._main_box = _make_box()

        self.set_child(scrolled_window)
        scrolled_window.set_child(self._main_box)

        for entry in self._make_entries():
            self._main_box.append(entry)

    def _connect_signals(self):
        event_connect(Event.LOAD_APP, self._load_app)

    def _make_entries(self) -> [LaunchEntry]:
        entries = []
        if not self._current_app: return entries
        app_entries = self.model.get_app_launch_menu(self._current_app.id)
        if not app_entries: return entries
        for i, entry in enumerate(app_entries):
            entries.append(LaunchEntry(app_entries[entry], i))
        return entries

    def _load_app(self, app: App):
        self._current_app = app
        self._make_widgets()
