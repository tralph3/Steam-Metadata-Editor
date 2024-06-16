from gi.repository import Gtk


def compose_entry_box(label: str, placeholder: str=None, editable: bool=True, icon: str=None) -> (Gtk.Box, Gtk.Entry):
    box = _make_box()
    label = _make_label(label)
    entry = _make_entry(placeholder, editable, icon)
    box.append(label)
    box.append(entry)
    return (box, entry)

def _make_box() -> Gtk.Box:
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, spacing=5)

def _make_label(label: str) -> Gtk.Label:
    label = Gtk.Label(label=label.upper(), vexpand=False, halign=Gtk.Align.START)
    label.set_css_classes(['entry_title'])
    return label

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

def clean_string(string: str) -> str:
    return ''.join(char for char in string if char.isalnum()).lower()
