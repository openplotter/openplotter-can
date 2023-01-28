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

import time, os, subprocess, ujson, sys
from openplotterSettings import language
from openplotterSettings import platform

class Start():
	def __init__(self, conf, currentLanguage):
		self.initialMessage = ''

	def start(self):
		green = '' 
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-can',currentLanguage)
		output = subprocess.check_output('ip -j a', shell=True).decode(sys.stdin.encoding)
		data = ujson.loads(output)
		self.canList = []
		for i in data:
			if 'canable' in i['ifname']: self.canList.append(i['ifname'])
			elif 'can' in i['ifname']: self.canList.append(i['ifname'])
		if self.canList: self.initialMessage = _('Checking CAN devices...')
		else: self.initialMessage = ''

	def check(self):
		platform2 = platform.Platform()
		green = ''
		black = '' 
		red = '' 

		try:
			setting_file = platform2.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except: data = {}

		for i in self.canList:
			exists = False
			if 'pipedProviders' in data:
				for ii in data['pipedProviders']:
					if ii['pipeElements'][0]['options']['subOptions']['type']=='canbus-canboatjs':
						if i == ii['pipeElements'][0]['options']['subOptions']['interface']: exists = True
			if not exists: 
				msg =  _('There is no Signal K connection for interface: ')+ i
				if not red: red = msg
				else: red+= '\n    '+msg
			else:
				if not black: black = i
				else: black += ' | ' + i

		if platform2.isRPI:
			if platform2.isInstalled('raspi-config'):
				for i in self.canList:
					if 'can' in i and 'canable' not in i:
						output = subprocess.check_output('raspi-config nonint get_spi', shell=True).decode(sys.stdin.encoding)
						if '1' in output:
							msg =_('Please enable SPI interface in Preferences -> Raspberry Pi configuration -> Interfaces.')
							if not red: red = msg
							else: red+= '\n    '+msg

		return {'green': green,'black': black,'red': red}
