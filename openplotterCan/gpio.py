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
			self.gpio = gpio.Gpio()
			gpioMap = self.gpio.gpioMap
			mcp2515 = []
			interruptMcp25150 = []
			interruptMcp2515 = []
			mcp251xfd = []
			interruptMcp251xfd0 = []
			interruptMcp251xfd = []
			try: file = open('/boot/firmware/config.txt', 'r')
			except: file = open('/boot/config.txt', 'r')
			while True:
				line = file.readline()
				if not line: break
				if 'dtoverlay=mcp2515' in line:
					line = line.rstrip()
					lList = line.split(',')
					for i in lList:
						if 'dtoverlay=mcp2515-can0' in i: mcp2515.append('24')
						if 'dtoverlay=mcp2515-can1' in i: mcp2515.append('26')
						if 'interrupt' in i:
							iList = i.split('=')
							interruptMcp25150.append('GPIO '+iList[1])
				if 'dtoverlay=mcp251xfd' in line:
					line = line.rstrip()
					lList = line.split(',')
					for i in lList:
						if 'spi0-0' in i: mcp251xfd.append('24')
						if 'spi0-1' in i: mcp251xfd.append('26')
						if 'spi1-0' in i: mcp251xfd.append('12')
						if 'spi1-1' in i: mcp251xfd.append('11')
						if 'interrupt' in i:
							iList = i.split('=')
							interruptMcp251xfd0.append('GPIO '+iList[1])

			if interruptMcp25150:
				for i in interruptMcp25150:
					for ii in gpioMap:
						if i == ii['BCM']: interruptMcp2515.append(ii['physical'])
			if interruptMcp251xfd0:
				for i in interruptMcp251xfd0:
					for ii in gpioMap:
						if i == ii['BCM']: interruptMcp251xfd.append(ii['physical'])

			if mcp2515 or mcp251xfd:
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'1'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'6'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'9'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'14'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'17'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'20'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'25'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'30'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'34'})
				self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'39'})
				if '24' in mcp2515 or '26' in mcp2515 or '24' in mcp251xfd or '26' in mcp251xfd:
					self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'19'})
					self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'21'})
					self.used.append({'app':'CAN', 'id':'MCP2515/MCP251xfd', 'physical':'23'})
				if '12' in mcp251xfd or '11' in mcp251xfd:
					self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'35'})
					self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'38'})
					self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'40'})
				for i in mcp2515:
					self.used.append({'app':'CAN', 'id': 'MCP2515', 'physical':i})
				for i in interruptMcp2515:
					self.used.append({'app':'CAN', 'id': 'MCP2515', 'physical':i})
				for i in mcp251xfd:
					self.used.append({'app':'CAN', 'id': 'MCP251xfd', 'physical':i})
				for i in interruptMcp251xfd:
					self.used.append({'app':'CAN', 'id': 'MCP251xfd', 'physical':i})

		return self.used