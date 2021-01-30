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
			connection_fd = []
			interrupt0_fd = []
			try: file = open('/boot/config.txt', 'r')
			except: file = open('/boot/firmware/config.txt', 'r')
			while True:
				line = file.readline()
				if not line: break
				if line.strip()[0:1] != '#':				
					if 'dtoverlay=mcp2515' in line:
						line = line.rstrip()
						lList = line.split(',')
						for i in lList:
							if 'dtoverlay=mcp2515-can0' in i: connection.append('24')
							if 'dtoverlay=mcp2515-can1' in i: connection.append('26')
							if 'interrupt' in i:
								iList = i.split('=')
								interrupt0.append('GPIO '+iList[1])
					if 'dtoverlay=mcp251xfd,' in line:
						line = line.rstrip()
						lList = line.split(',')
						for i in lList:
							if i == 'spi0-0': connection_fd.append('24')   #SPI0 CE0
							elif i == 'spi0-1': connection_fd.append('26') #SPI0 CE1
							elif i == 'spi1-0': connection_fd.append('12') #SPI1 CE0
							elif i == 'spi1-1': connection_fd.append('11') #SPI1 CE1

							if 'spi0' in i:
								self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'19'}) #SPI1 MOSI
								self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'21'}) #SPI0 MISO
								self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'23'}) #SPI1 SCLK
							elif 'spi1' in i:
								self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'38'}) #SPI1 MOSI
								self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'35'}) #SPI0 MISO
								self.used.append({'app':'CAN', 'id':'MCP251xfd', 'physical':'40'}) #SPI1 SCLK
								
							if 'interrupt' in i:
								iList = i.split('=')
								interrupt0_fd.append('GPIO '+iList[1])								
			if interrupt0:
				self.gpio = gpio.Gpio()
				gpioMap = self.gpio.gpioMap
				interrupt = []
				for i in interrupt0:
					for ii in gpioMap:
						if i == ii['BCM']: interrupt.append(ii['physical'])

			if interrupt0_fd:
				self.gpio = gpio.Gpio()
				gpioMap = self.gpio.gpioMap
				interrupt_fd = []
				for i in interrupt0_fd:
					for ii in gpioMap:
						if i == ii['BCM']: interrupt_fd.append(ii['physical'])

			self.used.append({'app':'CAN', 'id':'Power', 'physical':'1'})
			self.used.append({'app':'CAN', 'id':'Power', 'physical':'2'})
			self.used.append({'app':'CAN', 'id':'Power', 'physical':'4'})
			self.used.append({'app':'CAN', 'id':'Power', 'physical':'17'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'6'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'9'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'14'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'20'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'25'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'30'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'34'})
			self.used.append({'app':'CAN', 'id':'Ground', 'physical':'39'})

			if connection and interrupt:
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'19'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'21'})
				self.used.append({'app':'CAN', 'id':'MCP2515', 'physical':'23'})
				for i in connection:
					self.used.append({'app':'CAN', 'id': 'MCP2515', 'physical':i})
				for i in interrupt:
					self.used.append({'app':'CAN', 'id': 'MCP2515', 'physical':i})
			
			if connection_fd and interrupt_fd:
				for i in connection_fd:
					self.used.append({'app':'CAN', 'id': 'MCP251xfd', 'physical':i})
				for i in interrupt_fd:
					self.used.append({'app':'CAN', 'id': 'MCP251xfd', 'physical':i})
		
		return self.used