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

import geoclue
import dbus
from datetime import date

class LocalnetPreferencesDialog:

    def __init__(self):

        self.bus = dbus.SessionBus()

        self.uifile = "localnet-preferences.ui"

        builder = gtk.Builder()
        builder.add_from_file(self.uifile)

        builder.connect_signals({
          "on_edit_button_activate" : self.on_edit_button_activate,
          "on_close_button_clicked" : self.on_dialog_close,
          })

        self.address_treeview = builder.get_object("address_treeview")
        #self.provider_treeview = builder.get_object("provider_treeview")
        self.edit_button = builder.get_object("edit_button")

        self.create_general_tab()

        self.dialog = builder.get_object("localnet_preferences_dialog")
        self.dialog.show ()

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

        try:
            localnet = self.bus.get_object('org.freedesktop.Geoclue.Providers.Localnet',
                '/org/freedesktop/Geoclue/Providers/Localnet')

            address = dbus.Interface(localnet, dbus_interface='org.freedesktop.Geoclue.Address')
            address.connect_to_signal("AddressChanged", self.address_changed)
        except Exception, e:
            print "D-Bus error: %s" % e

        try:
            self.address_changed (*address.GetAddress())
        except Exception, e:
            print e

    def address_changed (self, timestamp, address, accuracy):
        self.address_store = gtk.ListStore (str, str)
        self.address_store.set_sort_column_id (0, gtk.SORT_ASCENDING)

        for key, value in address.items():
          self.address_store.append([key, value])

        self.address_treeview.set_model (self.address_store)
        mydate = date.fromtimestamp(timestamp)

    def on_dialog_close (self, button):
        self.dialog.hide()

    def on_edit_button_activate (self):
        pass
