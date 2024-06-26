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
import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-can',currentLanguage)
	platform2 = platform.Platform()

	print(_('Installing canboat...'))
	try:
		os.chdir('/tmp')
		os.system('rm -rf canboat')
		os.system('git clone https://github.com/canboat/canboat.git')
		os.chdir('canboat')
		os.system('make')
		os.system('make install')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Adding openplotter-can-read service...'))
	try:
		fo = open('/etc/systemd/system/openplotter-can-read.service', "w")
		fo.write( '[Service]\nExecStart=openplotter-can-read\nStandardOutput=journal\nStandardError=journal\nWorkingDirectory=/home/'+conf2.user+'\nUser=root\n[Install]\nWantedBy=multi-user.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		subprocess.call(['systemctl', 'enable', 'openplotter-can-read.service'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Installing/Updating "Signal K to NMEA 2000" plugin...'))
	try:
		if platform2.skDir:
			subprocess.call(['npm', 'i', '--verbose', 'signalk-to-nmea2000'], cwd = platform2.skDir)
			subprocess.call(['chown', '-R', conf2.user, platform2.skDir])
			subprocess.call(['systemctl', 'stop', 'signalk.service'])
			subprocess.call(['systemctl', 'stop', 'signalk.socket'])
			subprocess.call(['systemctl', 'start', 'signalk.socket'])
			subprocess.call(['systemctl', 'start', 'signalk.service'])
		else: print(_('Failed. Please, install Signal K server.'))
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'can', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()