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
        self.addresses_treeview = builder.get_object("addresses_treeview")
        self.edit_button = builder.get_object("edit_button")

        self.create_general_tab()
        self.create_addresses_tab()

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

    def on_dialog_close (self, button):
        self.dialog.hide()

    def on_edit_button_activate (self):
        pass

    def create_addresses_tab (self):
        # Setup current address display

        cellrenderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn("Mac Address", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 0)
        self.addresses_treeview.append_column (column)

        cellrenderer = gtk.CellRendererText ()
        cellrenderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        column = gtk.TreeViewColumn("Address", cellrenderer)
        column.add_attribute(cellrenderer, 'text', 1)
        column.set_expand (True)
        self.addresses_treeview.append_column (column)

        self.addresses_store = gtk.ListStore (str, str)
        self.addresses_store.set_sort_column_id (0, gtk.SORT_ASCENDING)

        self.addresses_treeview.set_model (self.addresses_store)
        self.load_addresses ()

    def load_addresses (self):

        filename = os.path.expanduser("~/.config/geoclue-localnet-gateways")
        file = ConfigParser.RawConfigParser()
        file.read(filename)

        for section in file.sections ():
            address = {}
            try:
                address['street'] = file.get(section, 'street')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['street'] = file.get(section, 'street')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['area'] = file.get(section, 'area')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['locality'] = file.get(section, 'locality')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['region'] = file.get(section, 'region')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['country'] = file.get(section, 'country')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['country_code']  =file.get(section, 'countrycode')
            except ConfigParser.NoOptionError:
                pass
            try:
                address['postal_code'] = file.get(section, 'postalcode')
            except ConfigParser.NoOptionError:
                pass

            line = ""
            try:
                line += address['street'] + ", "
            except KeyError:
                pass
            try:
                line += address['area'] + ", "
            except KeyError:
                pass
            try:
                line += address['locality'] + ", "
            except KeyError:
                pass
            try:
                line += address['region'] + ", "
            except KeyError:
                pass
            try:
                line += address['country']
            except KeyError:
                pass

            self.addresses_store.append([section, line])
            address = None
