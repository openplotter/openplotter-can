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
import subprocess, configparser, time

def main():
	data_conf = configparser.ConfigParser()
	conf_file = '.openplotter/openplotter.conf'
	data_conf.read(conf_file)
	items = data_conf.get('CAN', 'canable')
	try: devices = eval(items)
	except: devices = []
	exists = False
	for i in devices:
		c = 0
		while True:
			process = subprocess.Popen(['slcand','-o','-s5','-S','921600',i[0],i[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = process.communicate()
			if err:
				if c >= 5: break
				else:
					time.sleep(5)
					c = c+1
			else:
				time.sleep(1)
				subprocess.Popen(['ip', 'link', 'set', i[1], 'up'])
				time.sleep(1)
				exists = True
				break
	while exists:
		time.sleep(10)

if __name__ == '__main__':
	main()
