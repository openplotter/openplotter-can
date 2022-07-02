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

import sys, subprocess, time

if sys.argv[1]=='start':
	subprocess.call(['systemctl', 'start', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.service'])
if sys.argv[1]=='stop':
	subprocess.call(['systemctl', 'stop', 'signalk.service'])
	subprocess.call(['systemctl', 'stop', 'signalk.socket'])
if sys.argv[1]=='restart':
	subprocess.call(['systemctl', 'stop', 'signalk.service'])
	subprocess.call(['systemctl', 'stop', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.service'])
if sys.argv[1]=='removeCanable':
	subprocess.Popen(['ip', 'link', 'set', sys.argv[3], 'down'])
	time.sleep(1)
	subprocess.Popen(['slcand','-S','921600', '-c',sys.argv[2],sys.argv[3]])
	time.sleep(1)
	subprocess.Popen(['killall','slcand'])
	time.sleep(1)
if sys.argv[1]=='removeCanable' or sys.argv[1]=='addCanable': 
	from openplotterSettings import conf
	conf2 = conf.Conf()
	items = conf2.get('CAN', 'canable')
	try: devices = eval(items)
	except: devices = []
	for i in devices:
		subprocess.Popen(['slcand','-o','-s5','-S','921600',i[0],i[1]])
		time.sleep(1)
		subprocess.Popen(['ip', 'link', 'set', i[1], 'up'])
		time.sleep(1)
 