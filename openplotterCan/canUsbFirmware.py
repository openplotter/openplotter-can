#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by e-sailing <https://github.com/e-sailing>
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

import fcntl, sys, os, time, tty, termios, pyudev, serial
from openplotterSettings import conf
from openplotterSettings import language

class raw(object):
	def __init__(self, stream):
		self.stream = stream
		self.fd = self.stream.fileno()
	def __enter__(self):
		self.original_stty = termios.tcgetattr(self.stream)
		tty.setcbreak(self.stream)
	def __exit__(self, type, value, traceback):
		termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

class nonblocking(object):
	def __init__(self, stream):
		self.stream = stream
		self.fd = self.stream.fileno()
	def __enter__(self):
		self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
	def __exit__(self, *args):
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-can',currentLanguage)

	context = pyudev.Context()
	monitor = pyudev.Monitor.from_netlink(context)
	monitor.filter_by(subsystem='tty')
	print(_('Please connect (or disconnect and reconnect) the CAN-USB adapter'))


	for device in iter(monitor.poll, None):
		if device.action == 'add':
			value = device.get('DEVPATH')
			port = value[len(value) - value.find('/tty'):]
			port = '/dev/'+port[port.rfind('/') + 1:]
			print(port)
			try:
				ser = serial.Serial(port, 9600, timeout=0.5)
			except:
				print(_('Can not open serial device (CAN-USB) connected on: ')+port)
				sys.exit(0)
			ser.write(('0').encode())
			time.sleep(0.2)
			sertext=ser.readline().decode()
			if len(sertext)>=1:
				c='0'
				while c!='9':
					i=20
					while i>0:
						if ser.inWaiting():
							sertext=ser.readline().decode()
							print(sertext[:-1])
						else:
							i-=1
							time.sleep(0.05)
					i=180
					with raw(sys.stdin):
						with nonblocking(sys.stdin):
							while i>0:
								try:
									c = sys.stdin.read(1)
									#print(i,c)
									if c in ['1','2','3','4','5','6','7','8','9','0']:
										ser.write(c.encode())
										i=-5
								except IOError:
									print('Error')

								time.sleep(.1)
								i-=1
							if i>-2:
								ser.write(('0').encode())
			sys.exit(0)

if __name__ == '__main__':
	main()