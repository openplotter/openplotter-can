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

import ujson

class SerialPorts:
	def __init__(self,conf):
		self.conf = conf
		self.connections = []
		# {'app':'xxx', 'id':'xxx', 'data':'NMEA0183/NMEA2000/SignalK', 'device': '/dev/xxx', "baudrate": nnnnnn, "enabled": True/False}

	def usedSerialPorts(self):
		items = self.conf.get('CAN', 'canable')
		try: devices = eval(items)
		except: devices = []

		for i in devices:
			self.connections.append({'app':'CAN Bus','id':i[1], 'data':'NMEA2000', 'device': i[0], 'baudrate': 921600, "enabled": True})

		return self.connections