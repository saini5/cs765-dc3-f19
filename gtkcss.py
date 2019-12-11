import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


def set_gtk_style(filename):
  # rb needed for python 3 support
  css = open(filename, 'rb')
  css_data = css.read()
  css.close()
  style_provider = Gtk.CssProvider()
  style_provider.load_from_data(css_data)

  Gtk.StyleContext.add_provider_for_screen(
      Gdk.Screen.get_default(),
      style_provider,
      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
  )
