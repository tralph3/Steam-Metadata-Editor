import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk, Gdk
from .main_window import MainWindow


class View(Adw.Application):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('src/view/style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(self.model, application=app)
        self.win.present()
