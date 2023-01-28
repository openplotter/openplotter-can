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

base = 'dtoverlay=mcp251xfd,'
connection = base
if sys.argv[2] == 'SPI0 CE0': connection += 'spi0-0'
elif sys.argv[2] == 'SPI0 CE1': connection += 'spi0-1'
elif sys.argv[2] == 'SPI1 CE0': connection += 'spi1-0'
elif sys.argv[2] == 'SPI1 CE1': connection += 'spi1-1'

config = '/boot/config.txt'
boot = '/boot'
try: file = open(config, 'r')
except:
	config = '/boot/firmware/config.txt'
	boot = '/boot/firmware'
	file = open(config, 'r')
file1 = open('config.txt', 'w')
exists = False

canCount = 0
while True:
	line = file.readline()
	if not line: break
	if line.strip()[0:1] != '#':
		if base in line: canCount+=1
		if connection in line:
			#print(line)
			exists = True
			if sys.argv[1]=='enable':
				file1.write(connection+',oscillator='+sys.argv[4]+',interrupt='+sys.argv[3]+'\n')
			else: canCount-=1
		else: file1.write(line)
	else: file1.write(line)

if not exists and sys.argv[1]=='enable': 
	file1.write(connection+',oscillator='+sys.argv[4]+',interrupt='+sys.argv[3]+'\n')
	canCount+=1

file.close()
file1.close()

if os.system('diff config.txt '+config+' > /dev/null'): os.system('mv config.txt '+boot)
else: os.system('rm -f config.txt')

os.system('rm -f /etc/network/interfaces.d/can*')
if canCount>0:
	for i in range(canCount):
		can = 'can'+str(i)
		interfaceFile = '/etc/network/interfaces.d/'+can
		file = open(interfaceFile, 'w')
		file.write('#physical can interfaces\nallow-hotplug '+can+'\niface '+can+' can static\nbitrate 250000\ndown /sbin/ip link set $IFACE down\nup /sbin/ifconfig $IFACE txqueuelen 10000')
		file.close()