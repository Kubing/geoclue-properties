# -*- coding: utf-8 -*-

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gobject
except:
    print "Can't import Gtk"
    sys.exit(1)

import geoclue
import os

class AddressDialog:

    def __init__(self, title, description, address = None):

        path = os.path.dirname(os.path.abspath(__file__))
        self.uifile = os.path.join(path, "address-dialog.ui")

        builder = gtk.Builder()
        builder.add_from_file(self.uifile)

        builder.connect_signals({
          "on_save_button_clicked" : self.on_save_button_clicked,
          "on_cancel_button_clicked" : self.on_dialog_close,
          })

        self.dialog = builder.get_object("address_dialog")
        self.description_label = builder.get_object("description_label")
        self.entry_street = builder.get_object("entry_street")
        self.entry_area = builder.get_object("entry_area")
        self.entry_locality = builder.get_object("entry_locality")
        self.entry_region = builder.get_object("entry_region")
        self.entry_country = builder.get_object("entry_country")
        self.entry_countrycode = builder.get_object("entry_countrycode")

        self.address = address
        try:
            self.entry_street.set_text(address['street'])
        except KeyError:
            pass
        try:
            self.entry_area.set_text(address['area'])
        except KeyError:
            pass
        try:
            self.entry_locality.set_text(address['locality'])
        except KeyError:
            pass
        try:
            self.entry_region.set_text(address['region'])
        except KeyError:
            pass
        try:
            self.entry_country.set_text(address['country'])
        except KeyError:
            pass
        try:
            self.entry_countrycode.set_text(address['countrycode'])
        except KeyError:
            pass

        self.dialog.set_title (title)
        self.description_label.set_text(description)

    def on_dialog_close (self, button):
        self.dialog.hide()
        self.dialog.response (gtk.RESPONSE_CANCEL)

    def on_save_button_clicked (self, button):

        address = {}
        address['locality'] = self.entry_locality.get_text()
        address['country'] = self.entry_country.get_text()

        if address['locality'] == "" and address['country'] == "":

          dialog = gtk.MessageDialog (self.dialog, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
              gtk.BUTTONS_CLOSE, "You must fill locality and country.")
          dialog.set_title("Incomplete data")
          dialog.run()
          dialog.hide()
          return

        address['street'] = self.entry_street.get_text()
        address['area'] = self.entry_area.get_text()
        address['region'] = self.entry_region.get_text()
        address['country'] = self.entry_country.get_text()
        address['countrycode'] = self.entry_countrycode.get_text()
        self.address = address

        self.dialog.hide()
        self.dialog.response (gtk.RESPONSE_OK)

    def run (self):
        return self.dialog.run ()
