#!/usr/bin/env python

import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
except:
    print "Can't import Gtk"
    sys.exit(1)

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import geoclue
from datetime import date

DBusGMainLoop(set_as_default=True)

class GeocluePropertiesDialog:
    """This is an Hello World GTK application"""

    def __init__(self):

        self.bus = dbus.SessionBus()

        self.uifile = "geoclue-properties.ui"

        builder = gtk.Builder()
        builder.add_from_file(self.uifile)

        builder.connect_signals({
          "on_properties_dialog_close" : gtk.main_quit,
          "on_close_button_clicked": gtk.main_quit,
          })

        self.dialog = builder.get_object("properties_dialog")

        # Setup current address display
        self.address_provider_label = builder.get_object("address_provider_label")
        self.address_treeview = builder.get_object("address_treeview")

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Field", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 0)
        self.address_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Value", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 1)
        self.address_treeview.append_column (column)

        # Setup current position display
        self.position_provider_label = builder.get_object("position_provider_label")
        self.position_treeview = builder.get_object("position_treeview")

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Field", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 0)
        self.position_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Value", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 1)
        self.position_treeview.append_column (column)

        try:
            master = self.bus.get_object('org.freedesktop.Geoclue.Master',
                           '/org/freedesktop/Geoclue/Master')
            client = self.bus.get_object('org.freedesktop.Geoclue.Master', master.Create())
            client.connect_to_signal("AddressProviderChanged", self.address_provider_changed)
            client.connect_to_signal("PositionProviderChanged", self.position_provider_changed)

            address = dbus.Interface(client, dbus_interface='org.freedesktop.Geoclue.Address')
            address.connect_to_signal("AddressChanged", self.address_changed)
            client.AddressStart()

            position = dbus.Interface(client, dbus_interface='org.freedesktop.Geoclue.Position')
            position.connect_to_signal("PositionChanged", self.position_changed)
            client.PositionStart()
        except Exception, e:
            print "D-Bus error: %s" % e

        try:
            self.address_changed (*address.GetAddress())
        except Exception, e:
            print e

        try:
            current_position = position.GetPosition()
            self.position_changed (*position)
        except Exception, e:
            print e

        client.SetRequirements(geoclue.ACCURACY_LEVEL_NONE, 0, False, geoclue.RESOURCE_ALL)

        self.dialog = builder.get_object("properties_dialog")
        self.dialog.show ()

    def address_provider_changed (self, name, description, service, path):
        self.address_provider_label.set_text(name)

    def position_provider_changed (self, name, description, service, path):
        self.position_provider_label.set_text(name)

    def address_changed (self, timestamp, address, accuracy):
        self.address_store = gtk.ListStore (str, str)
        self.address_store.set_sort_column_id (0, gtk.SORT_ASCENDING)

        for key, value in address.items():
          self.address_store.append([key, value])

        self.address_treeview.set_model (self.address_store)
        mydate = date.fromtimestamp(timestamp)

        print mydate
        print accuracy

    def position_changed (self, fields, timestamp, latitude, longitude, altitude, accuracy):
        self.position_store = gtk.ListStore (str, str)
        self.position_store.set_sort_column_id (0, gtk.SORT_ASCENDING)

        self.position_treeview.set_model (self.address_store)

        if fields & POSITION_FIELDS_LATITUDE:
            self.position_store.append(["Latitude", "%0.5f" % latitude])
        if fields & POSITION_FIELDS_LONGITUDE:
            self.position_store.append(["Longitude", "%0.5f" % longitude])
        if fields & POSITION_FIELDS_ALTITUDE:
            self.position_store.append(["Altitude", "%0.5f" % altitude])

if __name__ == "__main__":
    dialog = GeocluePropertiesDialog()
    gtk.main()
