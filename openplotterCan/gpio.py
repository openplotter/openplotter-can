#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-can>
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
import subprocess, sys
from openplotterSettings import gpio
from openplotterSettings import platform

class Gpio:
	def __init__(self,conf):
		self.conf = conf
		self.platform = platform.Platform()
		self.used = [] # {'app':'xxx', 'id':'xxx', 'physical':'n'}

	def usedGpios(self):
		if self.platform.isRPI:
			connection = []
			interrupt0 = []
			file = open('/boot/config.txt', 'r')
			while True:
				line = file.readline()
				if not line: break
				if 'dtoverlay=mcp2515' in line:
					line = line.rstrip()
					lList = line.split(',')
					for i in lList:
						if 'dtoverlay=mcp2515-can0' in i: connection.append('24')
						if 'dtoverlay=mcp2515-can1' in i: connection.append('26')
						if 'interrupt' in i:
							iList = i.split('=')
							interrupt0.append('GPIO '+iList[1])
			if interrupt0:
				self.gpio = gpio.Gpio()
				gpioMap = self.gpio.gpioMap
				interrupt = []
				for i in interrupt0:
					for ii in gpioMap:
						if i == ii['BCM']: interrupt.append(ii['physical'])

			if connection and interrupt:
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'1'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'6'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'9'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'14'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'17'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'19'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'20'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'21'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'23'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'25'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'30'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'34'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'39'})
				for i in connection:
					self.used.append({'app':'CAN', 'id': 'MCP2515', 'physical':i})
				for i in interrupt:
					self.used.append({'app':'CAN', 'id': 'MCP2515', 'physical':i})

		return self.used