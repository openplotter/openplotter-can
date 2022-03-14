#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-can>
#                  
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from openplotterCan import version

setup (
	name = 'openplotterCan',
	version = version.version,
	description = 'OpenPlotter app to manage CAN BUS adapters',
	license = 'GPLv3',
	author="Sailoog",
	author_email='info@sailoog.com',
	url='https://github.com/openplotter/openplotter-can',
	packages=['openplotterCan'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-can=openplotterCan.openplotterCan:main','CAN-USB-firmware=openplotterCan.canUsbFirmware:main','openplotter-can-read=openplotterCan.openplotterCanRead:main','canPostInstall=openplotterCan.canPostInstall:main','canPreUninstall=openplotterCan.canPreUninstall:main']},
	data_files=[('share/applications', ['openplotterCan/data/openplotter-can.desktop']),('share/pixmaps', ['openplotterCan/data/openplotter-can.png']),],
	)
