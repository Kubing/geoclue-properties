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
from datetime import date
import ConfigParser

import geoclue
from address_dialog import AddressDialog

class ManualPreferencesDialog:

    def __init__(self, provider):
        self.provider = provider

        self.bus = dbus.SessionBus()

        self.uifile = "manual-preferences.ui"

        builder = gtk.Builder()
        builder.add_from_file(self.uifile)

        builder.connect_signals({
          "on_edit_current_button_clicked" : self.on_edit_current_button_clicked,
          "on_close_button_clicked" : self.on_dialog_close,
          })

        self.address_treeview = builder.get_object("address_treeview")

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
            manual = self.provider.get_proxy()

            address = dbus.Interface(manual, dbus_interface='org.freedesktop.Geoclue.Address')
            address.connect_to_signal("AddressChanged", self.address_changed)
        except Exception, e:
            print "D-Bus error: %s" % e

        try:
            self.address_changed (*address.GetAddress())
        except Exception, e:
            print e

    def address_changed (self, timestamp, address, accuracy):

        self.update_current_address(address)

    def update_current_address (self, address):
        self.address_store = gtk.ListStore (str, str)
        self.address_store.set_sort_column_id (0, gtk.SORT_ASCENDING)

        for key, value in address.items():
          self.address_store.append([key, value])

        self.address_treeview.set_model (self.address_store)
        self.address = address

    def on_dialog_close (self, button):
        self.dialog.hide()

    def on_edit_current_button_clicked (self, selection):
        dialog = AddressDialog("New Address", "Enter the address associated with the current network.", self.address)
        response = dialog.run ()

        if response == gtk.RESPONSE_OK:
            try:
                manual = self.provider.get_proxy()
                manual.SetAddress (0, dialog.address)
            except Exception, e:
                print "D-Bus error: %s" % e
            #FIXME: the new address doesn't show up in the UI
            self.update_current_address (dialog.address)

