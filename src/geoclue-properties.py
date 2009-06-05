#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gobject
    import pango
except:
    print "Can't import Gtk"
    sys.exit(1)

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from datetime import date

import geoclue
from localnet_preferences import LocalnetPreferencesDialog
DBusGMainLoop(set_as_default=True)

class GeocluePropertiesDialog:

    def __init__(self):

        self.bus = dbus.SessionBus()

        self.uifile = "geoclue-properties.ui"

        builder = gtk.Builder()
        builder.add_from_file(self.uifile)

        builder.connect_signals({
          "on_properties_dialog_close" : gtk.main_quit,
          "on_close_button_clicked": gtk.main_quit,
          "on_preferences_button_clicked": self.on_preferences_button_clicked,
          })

        self.address_provider_label = builder.get_object("address_provider_label")
        self.address_treeview = builder.get_object("address_treeview")
        self.position_provider_label = builder.get_object("position_provider_label")
        self.position_treeview = builder.get_object("position_treeview")
        self.provider_treeview = builder.get_object("provider_treeview")
        self.preferences_button = builder.get_object("preferences_button")

        self.create_general_tab()
        self.create_provider_tab()

        self.dialog = builder.get_object("properties_dialog")
        self.dialog.show ()

    def create_provider_tab (self):
        cellrenderer = gtk.CellRendererText ()
        cellrenderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column = gtk.TreeViewColumn("Name", cellrenderer)
        column.add_attribute(cellrenderer, 'markup', 1)
        column.set_expand (True)
        self.provider_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Address", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 2)
        column.add_attribute(cellrenderer, 'visible', 3)
        cellrenderer.set_property('xalign', 0.5)
        self.provider_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Position", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 2)
        column.add_attribute(cellrenderer, 'visible', 4)
        cellrenderer.set_property('xalign', 0.5)
        self.provider_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Geocoding", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 2)
        column.add_attribute(cellrenderer, 'visible', 5)
        cellrenderer.set_property('xalign', 0.5)
        self.provider_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Rev. Geocoding", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 2)
        column.add_attribute(cellrenderer, 'visible', 6)
        cellrenderer.set_property('xalign', 0.5)
        self.provider_treeview.append_column (column)

        self.provider_store = gtk.ListStore (gobject.TYPE_PYOBJECT,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN)
        self.provider_store.set_sort_column_id (1, gtk.SORT_ASCENDING)

        path = "/usr/share/geoclue-providers/"
        dir = os.listdir(path)

        for filename in dir:
            (name, ext) = os.path.splitext(filename)

            if ext == ".provider":
                complete = os.path.join(path, filename)
                provider = geoclue.GeoclueProvider (complete)
                self.provider_store.append([provider,
                  provider.name, "✔",
                  provider.interfaces & geoclue.INTERFACE_ADDRESS,
                  provider.interfaces & geoclue.INTERFACE_POSITION,
                  provider.interfaces & geoclue.INTERFACE_GEOCODE,
                  provider.interfaces & geoclue.INTERFACE_REVERSE_GEOCODE,
                  ])

        self.provider_treeview.set_model (self.provider_store)
        selection = self.provider_treeview.get_selection ()
        selection.connect("changed", self.provider_selection_changed)

    def provider_selection_changed (self, selection):
        (model, iter) = selection.get_selected ()
        provider = model.get_value (iter, 0)

        if provider.name == "Manual" or provider.name == "Localnet":
            self.preferences_button.set_sensitive(True)
        else:
            self.preferences_button.set_sensitive(False)

    def on_preferences_button_clicked (self, button):
        selection = self.provider_treeview.get_selection()
        (model, iter) = selection.get_selected ()
        provider = model.get_value (iter, 0)

        if provider.name == "Localnet":
            dialog = LocalnetPreferencesDialog(provider)

    def create_general_tab (self):
        # Setup current address display

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Field", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 0)
        self.address_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Value", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 1)
        self.address_treeview.append_column (column)

        # Setup current position display
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
