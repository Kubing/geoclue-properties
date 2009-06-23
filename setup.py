#!/usr/bin/env python

from distutils.core import setup

def create_data_files():
    data_files = []

    # misc
    data_files.append(('share/applications', ['geoclue-properties.desktop']))
    return data_files

setup(name='Geoclue Properties',
      version='0.1',
      url='http://blog.pierlux.com/',
      description='A Geoclue configuration tool',
      author='Pierre-Luc Beaudoin',
      author_email='pierre-luc@pierlux.com',
      packages=['geoclueproperties'],
      package_data = {
         'geoclueproperties': [
            'geoclue-properties.ui',
            'address-dialog.ui',
            'localnet-preferences.ui',
            'manual-preferences.ui']
         },
      data_files = create_data_files(),
      scripts=['geoclue-properties',],
    )

