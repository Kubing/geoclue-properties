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

class LocalnetPreferencesDialog:

    def __init__(self, provider):
        self.provider = provider

        self.bus = dbus.SessionBus()

        self.uifile = "localnet-preferences.ui"

        builder = gtk.Builder()
        builder.add_from_file(self.uifile)

        builder.connect_signals({
          "on_add_button_clicked" : self.on_add_button_clicked,
          "on_edit_current_button_clicked" : self.on_edit_current_button_clicked,
          "on_edit_button_clicked" : self.on_edit_button_clicked,
          "on_remove_button_clicked" : self.on_remove_button_clicked,
          "on_close_button_clicked" : self.on_dialog_close,
          })

        self.address_treeview = builder.get_object("address_treeview")
        self.addresses_treeview = builder.get_object("addresses_treeview")
        self.edit_button = builder.get_object("edit_button")
        self.remove_button = builder.get_object("remove_button")

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
            localnet = self.provider.get_proxy()

            address = dbus.Interface(localnet, dbus_interface='org.freedesktop.Geoclue.Address')
            address.connect_to_signal("AddressChanged", self.address_changed)
        except Exception, e:
            print "D-Bus error: %s" % e

        try:
            self.address_changed (*address.GetAddress())
        except Exception, e:
            print e

    def address_changed (self, timestamp, address, accuracy):
        self.update_current_address (address)

    def update_current_address (self, address):
        self.address_store = gtk.ListStore (str, str)
        self.address_store.set_sort_column_id (0, gtk.SORT_ASCENDING)

        for key, value in address.items():
          self.address_store.append([key, value])

        self.address_treeview.set_model (self.address_store)
        self.address = address

    def on_dialog_close (self, button):
        self.dialog.hide()

    def on_edit_button_clicked (self):
        dialog = AddressDialog()
        print dialog.run ()

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

        selection = self.addresses_treeview.get_selection ()
        selection.connect("changed", self.addresses_selection_changed)

    def addresses_selection_changed (self, selection):
        (model, iter) = selection.get_selected ()

        if iter is None:
            pass
            #self.edit_button.set_sensitive(False)
            #self.remove_button.set_sensitive(False)
        else:
            #self.edit_button.set_sensitive(True)
            pass
            #self.remove_button.set_sensitive(True)

    def on_add_button_clicked (self, selection):
        pass

    def on_edit_current_button_clicked (self, selection):
        dialog = AddressDialog("New Address", "Enter the address associated with the current network.", self.address)
        response = dialog.run ()

        if response == gtk.RESPONSE_OK:
            try:
                localnet = self.provider.get_proxy()
                localnet.SetAddress (dialog.address)
            except Exception, e:
                print "D-Bus error: %s" % e
            #FIXME: the new address doesn't show up in the UI
            self.update_current_address (dialog.address)
            self.load_addresses ()

    def on_remove_button_clicked (self, selection):
        pass

    def load_addresses (self):
        self.addresses_store.clear()

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
