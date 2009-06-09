# Copyright (C) 2009 Pierre-Luc Beaudoin

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301  USA

import ConfigParser
import dbus

POSITION_FIELDS_NONE = 0
POSITION_FIELDS_LATITUDE = 1 << 0
POSITION_FIELDS_LONGITUDE = 1 << 1
POSITION_FIELDS_ALTITUDE = 1 << 2

ADDRESS_FIELD_STREET = "street"
ADDRESS_FIELD_AREA = "area"
ADDRESS_FIELD_LOCALITY = "locality"
ADDRESS_FIELD_REGION = "region"
ADDRESS_FIELD_COUNTRY = "country"

RESOURCE_NONE = 0
RESOURCE_NETWORK = 1 << 0
RESOURCE_CELL = 1 << 1
RESOURCE_GPS = 1 << 2
RESOURCE_ALL = (1 << 10) - 1

ACCURACY_LEVEL_NONE = 0
ACCURACY_LEVEL_COUNTRY = 1
ACCURACY_LEVEL_REGION = 2
ACCURACY_LEVEL_LOCALITY = 3
ACCURACY_LEVEL_POSTALCODE = 4
ACCURACY_LEVEL_STREET = 5
ACCURACY_LEVEL_DETAILED = 6

INTERFACE_NONE = 0
INTERFACE_ADDRESS = 1 << 0
INTERFACE_POSITION = 1 << 1
INTERFACE_GEOCODE = 1 << 2
INTERFACE_REVERSE_GEOCODE = 1 << 3

class GeoclueProvider():
    pass

    def __init__ (self, filename):
        '''
        Takes the path to a .provider file
        '''

        file = ConfigParser.RawConfigParser()
        file.read(filename)

        self.name = file.get('Geoclue Provider', 'Name')
        self.path = file.get('Geoclue Provider', 'Path')
        self.service = file.get('Geoclue Provider', 'Service')
        interfaces = file.get('Geoclue Provider', 'Interfaces').split(";")
        self.interfaces = INTERFACE_NONE

        for interface in interfaces:
            if interface == "org.freedesktop.Geoclue.Address":
               self.interfaces += INTERFACE_ADDRESS
            elif interface == "org.freedesktop.Geoclue.Position":
               self.interfaces += INTERFACE_POSITION
            elif interface == "org.freedesktop.Geoclue.Geocode":
               self.interfaces += INTERFACE_GEOCODE
            elif interface == "org.freedesktop.Geoclue.ReverseGeocode":
               self.interfaces += INTERFACE_REVERSE_GEOCODE
    def get_proxy (self):
        self.bus = dbus.SessionBus()
        return self.bus.get_object(self.service, self.path)
