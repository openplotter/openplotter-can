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

import sys, os

if sys.argv[2] == 'SPI0': connection = 'dtoverlay=mcp2515-can0'
elif sys.argv[2] == 'SPI1': connection = 'dtoverlay=mcp2515-can1'

file = open('/boot/config.txt', 'r')
file1 = open('config.txt', 'w')
exists = False
while True:
	line = file.readline()
	if not line: break
	if connection in line:
		exists = True
		if sys.argv[1]=='enable':
			file1.write(connection+',oscillator='+sys.argv[3]+',interrupt='+sys.argv[4]+'\n')
	else: file1.write(line)
if not exists and sys.argv[1]=='enable': file1.write(connection+',oscillator='+sys.argv[3]+',interrupt='+sys.argv[4]+'\n')
file.close()
file1.close()

if os.system('diff config.txt /boot/config.txt > /dev/null'): os.system('mv config.txt /boot')
else: os.system('rm -f config.txt')


os.system('rm -f /etc/network/interfaces.d/can*')
if sys.argv[5]:
	for i in range(int(sys.argv[5])):
		can = 'can'+str(i)
		interfaceFile = '/etc/network/interfaces.d/'+can
		file = open(interfaceFile, 'w')
		file.write('#physical can interfaces\nallow-hotplug '+can+'\niface '+can+' can static\nbitrate 250000\ndown /sbin/ip link set $IFACE down\nup /sbin/ifconfig $IFACE txqueuelen 10000')
		file.close()