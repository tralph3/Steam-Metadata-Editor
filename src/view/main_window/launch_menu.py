from gi.repository import Gtk, Adw
from view.objects import App
from view.events import Event, event_connect, event_emit
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
        description_box, self.description_entry = compose_entry_box("Description", "Unspecified")
        executable_box, self.execuable_entry = compose_entry_box("Executable", "Unspecified", False, "folder")
        workdir_box, self.workdir_entry = compose_entry_box("Working Directory", "Unspecified", False, "folder")
        arguments_box, self.arguments_entry = compose_entry_box("Launch Arguments", "Unspecified")
        delete_button = Gtk.Button()
        bottom_box = Gtk.Box()
        checkbutton_box = Gtk.Box(hexpand=True)
        self.windows_checkbutton = Gtk.CheckButton(label="Windows")
        self.mac_checkbutton = Gtk.CheckButton(label="Mac")
        self.linux_checkbutton = Gtk.CheckButton(label="Linux")

        delete_button.set_icon_name("edit-delete")
        delete_button.connect("clicked", self._delete_self)

        checkbutton_box.append(self.windows_checkbutton)
        checkbutton_box.append(self.mac_checkbutton)
        checkbutton_box.append(self.linux_checkbutton)
        bottom_box.append(checkbutton_box)
        bottom_box.append(delete_button)
        bottom_box.set_hexpand(True)

        self.append(description_box)
        self.append(executable_box)
        self.append(workdir_box)
        self.append(arguments_box)
        self.append(bottom_box)

    def _configure_widgets(self):
        css_class = ""
        if self.index % 2 == 0:
            css_class = "launch_entry_even"
        else:
            css_class = "launch_entry_odd"
        self.set_spacing(15)
        self.set_css_classes([css_class])
        self.description_entry.set_text(self.entry.get("description", ""))
        self.execuable_entry.set_text(self.entry.get("executable", ""))
        self.workdir_entry.set_text(self.entry.get("workingdir", ""))
        arguments = self.entry.get("arguments", "")
        if isinstance(arguments, int): arguments = ""
        self.arguments_entry.set_text(arguments)

        entry_oslist = self.entry.get("config", {}).get("oslist", "").lower()
        self.windows_checkbutton.set_active("windows" in entry_oslist)
        self.mac_checkbutton.set_active("macos" in entry_oslist)
        self.linux_checkbutton.set_active("linux" in entry_oslist)

    def _delete_self(self, *_):
        event_emit(Event.DELETE_LAUNCH_ENTRY, self)


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
        self._entries_box = _make_box()
        tool_bar = Adw.ToolbarView()
        action_bar = Gtk.ActionBar()

        add_button = Gtk.Button()
        add_button.set_icon_name("list-add")
        action_bar.pack_end(add_button)
        tool_bar.add_bottom_bar(action_bar)
        tool_bar.set_content(scrolled_window)

        self.set_child(tool_bar)
        scrolled_window.set_child(self._entries_box)

    def _connect_signals(self):
        event_connect(Event.LOAD_APP, self._load_app)
        event_connect(Event.DELETE_LAUNCH_ENTRY, self._delete_launch_entry)

    def _delete_launch_entry(self, entry: LaunchEntry):
        self._entries_box.remove(entry)

    def _make_entries(self) -> [LaunchEntry]:
        entries = []
        if not self._current_app: return entries
        app_entries = self.model.get_app_launch_menu(self._current_app.id)
        if not app_entries: return entries
        for i, entry in enumerate(app_entries):
            entries.append(LaunchEntry(app_entries[entry], i))
        return entries

    def _delete_all_entries_from_box(self):
        child = self._entries_box.get_first_child()
        while child:
            self._entries_box.remove(child)
            child = self._entries_box.get_first_child()

    def _load_app_entries(self):
        self._delete_all_entries_from_box()
        for entry in self._make_entries():
            self._entries_box.append(entry)

    def _load_app(self, app: App):
        self._current_app = app
        self._load_app_entries()
