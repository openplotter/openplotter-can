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

import wx, os, webbrowser, subprocess, socket, ujson
import wx.richtext as rt
import serial.tools.list_ports
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

import time, serial, codecs
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(__file__)
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-can',self.currentLanguage)

		wx.Frame.__init__(self, None, title=_('OpenPlotter CAN Bus'), size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-can.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		self.canUsbSetup = self.toolbar1.AddTool(103, _('CAN-USB Setup'), wx.Bitmap(self.currentdir+"/data/openplotter-24.png"))
		self.Bind(wx.EVT_TOOL, self.onCanUsbSetup, self.canUsbSetup)
		self.toolbar1.AddSeparator()
		self.AddSkCon = self.toolbar1.AddTool(104, _('Add SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onAddSkCon, self.AddSkCon)
		self.SKtoN2K = self.toolbar1.AddTool(105, _('SK Output'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onSKtoN2K, self.SKtoN2K)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.sk = wx.Panel(self.notebook)
		self.canable = wx.Panel(self.notebook)
		self.mcp2515 = wx.Panel(self.notebook)
		self.notebook.AddPage(self.sk, _('CAN-USB'))
		self.notebook.AddPage(self.canable, _('CAN-USB / CANable'))
		self.notebook.AddPage(self.mcp2515, _('MCP2515'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-24.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/usb.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/chip.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageSk()
		self.pageCanable()
		self.pageMcp2515()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()

		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:
			return
		if self.notebook.GetSelection() == 2 and not self.platform.isRPI:
			self.toolbar1.EnableTool(106,True)
			self.toolbar1.EnableTool(107,True)
		else:
			self.toolbar1.EnableTool(106,False)
			self.toolbar1.EnableTool(107,False)

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/can/can_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def pageSk(self):
		skLabel = wx.StaticText(self.sk, label='Actinsense NGT-1 (canboatjs)')
		self.listSKcan = wx.ListCtrl(self.sk, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listSKcan.InsertColumn(0, _('Serial Port'), width=200)
		self.listSKcan.InsertColumn(1, _('Baud Rate'), width=200)
		self.listSKcan.InsertColumn(2, _('SK connection ID'), width=200)
		self.listSKcan.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSKcanSelected)
		self.listSKcan.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSKcanDeselected)

		self.toolbar2 = wx.ToolBar(self.sk, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.editSkCon = self.toolbar2.AddTool(201, _('Edit SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onEditSkCon, self.editSkCon)
		self.RefreshSk = self.toolbar2.AddTool(202, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.onRefreshSk, self.RefreshSk)
		self.toolbar2.AddSeparator()
		self.SKcanTX = self.toolbar2.AddTool(203, _('Open device TX PGNs'), wx.Bitmap(self.currentdir+"/data/openplotter-24.png"))
		self.Bind(wx.EVT_TOOL, self.onSKcanTX, self.SKcanTX)

		h1 = wx.BoxSizer(wx.VERTICAL)
		h1.AddSpacer(5)
		h1.Add(skLabel, 0, wx.LEFT, 10)
		h1.AddSpacer(5)
		h1.Add(self.listSKcan, 1, wx.EXPAND, 0)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(h1, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar2, 0)
		self.sk.SetSizer(sizer)

		self.readSk()

	def readSk(self):
		self.sklist = []
		try:
			setting_file = self.platform.skDir+'/settings.json'
			data = ''
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
			if 'pipedProviders' in data:
				for i in data['pipedProviders']:
					if i['pipeElements'][0]['options']['subOptions']['type']=='ngt-1-canboatjs':
						self.sklist.append([i['pipeElements'][0]['options']['subOptions']['device'],i['pipeElements'][0]['options']['subOptions']['baudrate'],i['id'],i['enabled']])
		except:pass

		self.listSKcan.DeleteAllItems()
		isEmpty = True
		for ii in self.sklist:
			self.listSKcan.Append([ii[0],ii[1],str(ii[2])])
			isEmpty = False
			if ii[3]: self.listSKcan.SetItemBackgroundColour(self.listSKcan.GetItemCount()-1,(0,191,255))
		if isEmpty:
			self.listSKcan.Append(['','','!' + _('Add SK Connection')])

		self.toolbar2.EnableTool(201,False)
		self.toolbar2.EnableTool(203,False)
		self.SetStatusText('')

	def onCanUsbSetup(self,e):
		subprocess.call(['pkill', '-15', 'CAN-USB-firmware'])
		subprocess.call(['x-terminal-emulator','-e', 'CAN-USB-firmware'])

	def onAddSkCon(self,e):
		if self.platform.skPort: 
			url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
			webbrowser.open(url, new=2)
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def onSKtoN2K(self,e):
		if self.platform.skPort: 
			if self.platform.isSKpluginInstalled('signalk-to-nmea2000'):
				url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea2000'
			else: 
				self.ShowStatusBarRED(_('Please install "signalk-to-nmea2000" Signal K app'))
				url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/appstore/apps'
			webbrowser.open(url, new=2)
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def onEditSkCon(self,e):
		selected = self.listSKcan.GetFirstSelected()
		if selected == -1: return
		skId = self.listSKcan.GetItemText(selected, 2)
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/'+skId
		webbrowser.open(url, new=2)

	def onRefreshSk(self,e):
		self.readSk()

	def onSKcanTX(self,e):
		selected = self.listSKcan.GetFirstSelected()
		if selected == -1: return
		skId = self.listSKcan.GetItemText(selected, 2)
		device = self.listSKcan.GetItemText(selected, 0)
		bauds = self.listSKcan.GetItemText(selected, 1)
		if self.enable_disable_device(skId,0): self.restart_SK(_('Disabling device and restarting Signal K server... '))
		dlg = openPGNs(self,device,bauds)
		res = dlg.ShowModal()
		dlg.Destroy()
		if self.enable_disable_device(skId,1): self.restart_SK(_('Enabling device and restarting Signal K server... '))

	def enable_disable_device(self,deviceId,enable):
		write = False
		try:
			count = 0
			setting_file = self.platform.skDir+'/settings.json'
			data = ''
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
			for i in data['pipedProviders']:
				if i['id'] == deviceId:
					if enable == 1:
						if i['enabled'] == False:
							write = True
							data['pipedProviders'][count]['enabled'] = True
					elif enable == 0:
						if i['enabled'] == True:
							write = True
							data['pipedProviders'][count]['enabled'] = False
				count = count + 1
			if write:
				data2 = ujson.dumps(data, indent=4, sort_keys=True)
				file = open(setting_file, 'w')
				file.write(data2)
				file.close()
		except: pass

		return write
		
	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'stop'])
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'start'])
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.readSk()
		self.ShowStatusBarGREEN(_('Signal K server restarted'))

	def onListSKcanSelected(self,e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.toolbar2.EnableTool(201,True)
		self.toolbar2.EnableTool(203,True)

	def onListSKcanDeselected(self,e):
		self.toolbar2.EnableTool(201,False)
		self.toolbar2.EnableTool(203,False)

		#####################################################

	def pageCanable(self):
		canableLabel = wx.StaticText(self.canable, label='Canbus (canboatjs)')
		self.listCanable = wx.ListCtrl(self.canable, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listCanable.InsertColumn(0, _('Serial Port'), width=200)
		self.listCanable.InsertColumn(1, _('Interface'), width=150)
		self.listCanable.InsertColumn(2, _('SK connection ID'), width=200)
		self.listCanable.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListCanableSelected)
		self.listCanable.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListCanableDeselected)

		self.toolbar4 = wx.ToolBar(self.canable, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.editCanableCon = self.toolbar4.AddTool(401, _('Edit SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onEditCanableCon, self.editCanableCon)
		self.refreshCanable = self.toolbar4.AddTool(402, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.onRefreshCanable, self.refreshCanable)
		self.toolbar4.AddSeparator()
		self.addCanable = self.toolbar4.AddTool(403, _('Add SocketCAN device'), wx.Bitmap(self.currentdir+"/data/usb.png"))
		self.Bind(wx.EVT_TOOL, self.onAddCanable, self.addCanable)
		self.removeCanable = self.toolbar4.AddTool(404, _('Remove SocketCAN device'), wx.Bitmap(self.currentdir+"/data/usb.png"))
		self.Bind(wx.EVT_TOOL, self.onRemoveCanable, self.removeCanable)

		h1 = wx.BoxSizer(wx.VERTICAL)
		h1.AddSpacer(5)
		h1.Add(canableLabel, 0, wx.LEFT, 10)
		h1.AddSpacer(5)
		h1.Add(self.listCanable, 1, wx.EXPAND, 0)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(h1, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar4, 0)
		self.canable.SetSizer(sizer)

		self.readCanable()

	def readCanable(self):
		self.listCanable.DeleteAllItems()
		try:
			setting_file = self.platform.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except: data = {}

		items = self.conf.get('CAN', 'canable')
		try: devices = eval(items)
		except: devices = []

		for ii in devices:
			device = ii[0]
			interface = ii[1]
			skId = '!' + _('Add SK Connection')
			enabled = False
			if 'pipedProviders' in data:
				for i in data['pipedProviders']:
					if i['pipeElements'][0]['options']['subOptions']['type']=='canbus-canboatjs':
						if interface == i['pipeElements'][0]['options']['subOptions']['interface']: 
							skId = i['id']
							enabled = i['enabled']
			self.listCanable.Append([device,interface,skId])
			if skId and enabled: self.listCanable.SetItemBackgroundColour(self.listCanable.GetItemCount()-1,(0,191,255))

		if 'pipedProviders' in data:
			for i in data['pipedProviders']:
				if i['pipeElements'][0]['options']['subOptions']['type']=='canbus-canboatjs':
					if not 'can' in i['pipeElements'][0]['options']['subOptions']['interface'] or 'canable' in i['pipeElements'][0]['options']['subOptions']['interface']:
						interface = i['pipeElements'][0]['options']['subOptions']['interface']
						skId = i['id']
						exists = False
						for ii in range(self.listCanable.GetItemCount()):
							if interface == self.listCanable.GetItemText(ii, 1): exists = True
						if not exists: self.listCanable.Append(['',interface,skId])

		self.toolbar4.EnableTool(401,False)
		self.toolbar4.EnableTool(404,False)
		self.SetStatusText('')

	def onEditCanableCon(self,e):
		selected = self.listCanable.GetFirstSelected()
		if selected == -1: return
		skId = self.listCanable.GetItemText(selected, 2)
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/'+skId
		webbrowser.open(url, new=2)

	def onRefreshCanable(self,e):
		self.readCanable()

	def onRemoveCanable(self,e):
		selected = self.listCanable.GetFirstSelected()
		if selected == -1: return
		devicesNew = []
		device = self.listCanable.GetItemText(selected, 0)
		interface = self.listCanable.GetItemText(selected, 1)
		items = self.conf.get('CAN', 'canable')
		try: devices = eval(items)
		except: devices = []
		for i in devices:
			if device != i[0]: devicesNew.append(i)
		self.ShowStatusBarYELLOW(_('Restarting CANable interfaces...'))
		self.conf.set('CAN', 'canable', str(devicesNew))
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'removeCanable', device, interface])
		self.readCanable()
		self.restart_SK(0)

	def onAddCanable(self,e):
		dlg = AddPort()
		res = dlg.ShowModal()
		restart = False
		if res == wx.ID_OK:
			device = dlg.port.GetStringSelection()
			items = self.conf.get('CAN', 'canable')
			try: devices = eval(items)
			except: devices = []
			for i in devices:
				if device == i[0]:
					self.ShowStatusBarRED(_('This serial port already exists'))
					dlg.Destroy()
					return
			c = 0
			while True:
				interface = 'canable'+str(c)
				exists = False
				for i in devices:
					if interface == i[1]: exists = True
				if not exists: break
				else: c = c +1
			interface = 'canable'+str(c)
			devices.append([device,interface])
			self.ShowStatusBarYELLOW(_('Restarting CANable interfaces...'))
			self.conf.set('CAN', 'canable', str(devices))
			subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'addCanable', device, interface])
			restart = True
		dlg.Destroy()
		self.readCanable()
		if restart: self.restart_SK(0)

	def onListCanableSelected(self,e):
		selected = self.listCanable.GetFirstSelected()
		if selected == -1: return
		self.toolbar4.EnableTool(404,True)
		skId = self.listCanable.GetItemText(selected, 2)
		device = self.listCanable.GetItemText(selected, 0)
		if skId: self.toolbar4.EnableTool(401,True)
		else: self.toolbar4.EnableTool(401,False)
		if device: self.toolbar4.EnableTool(404,True)
		else: self.toolbar4.EnableTool(404,False)

	def onListCanableDeselected(self,e):
		self.toolbar4.EnableTool(401,False)
		self.toolbar4.EnableTool(404,False)

		#####################################################

	def pageMcp2515(self):
		if self.platform.isRPI:
			mcp2515Label = wx.StaticText(self.mcp2515, label='Canbus (canboatjs)')
			self.listMcp2515 = wx.ListCtrl(self.mcp2515, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
			self.listMcp2515.InsertColumn(0, _('Connection'), width=110)
			self.listMcp2515.InsertColumn(1, _('Oscillator'), width=110)
			self.listMcp2515.InsertColumn(2, _('Interrupt'), width=110)
			self.listMcp2515.InsertColumn(3, _('Interface'), width=110)
			self.listMcp2515.InsertColumn(4, _('SK connection ID'), width=150)
			self.listMcp2515.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListlistMcp2515Selected)
			self.listMcp2515.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListlistMcp2515Deselected)

			self.toolbar3 = wx.ToolBar(self.mcp2515, style=wx.TB_TEXT | wx.TB_VERTICAL)
			self.editMcp2515SkCon = self.toolbar3.AddTool(301, _('Edit SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
			self.Bind(wx.EVT_TOOL, self.onEditMcp2515SkCon, self.editMcp2515SkCon)
			self.refreshMcp2515 = self.toolbar3.AddTool(302, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
			self.Bind(wx.EVT_TOOL, self.onRefreshMcp2515, self.refreshMcp2515)
			self.toolbar3.AddSeparator()
			self.addMcp2515 = self.toolbar3.AddTool(303, _('Add device'), wx.Bitmap(self.currentdir+"/data/chip.png"))
			self.Bind(wx.EVT_TOOL, self.onAddMcp2515, self.addMcp2515)
			self.removeMcp2515 = self.toolbar3.AddTool(304, _('Remove device'), wx.Bitmap(self.currentdir+"/data/chip.png"))
			self.Bind(wx.EVT_TOOL, self.onRemoveMcp2515, self.removeMcp2515)

			h1 = wx.BoxSizer(wx.VERTICAL)
			h1.AddSpacer(5)
			h1.Add(mcp2515Label, 0, wx.LEFT, 10)
			h1.AddSpacer(5)
			h1.Add(self.listMcp2515, 1, wx.EXPAND, 0)

			sizer = wx.BoxSizer(wx.HORIZONTAL)
			sizer.Add(h1, 1, wx.EXPAND, 0)
			sizer.Add(self.toolbar3, 0)
			self.mcp2515.SetSizer(sizer)

			self.readMcp2515()

	def readMcp2515(self):
		self.listMcp2515.DeleteAllItems()
		try:
			setting_file = self.platform.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except: data = {}
		file = open('/boot/config.txt', 'r')
		while True:
			line = file.readline()
			if not line: break
			if 'dtoverlay=mcp2515' in line:
				connection = ''
				oscillator = ''
				interrupt = ''
				skId = '!' + _('Add SK Connection')
				enabled = False
				line = line.rstrip()
				lList = line.split(',')
				for i in lList:
					if 'dtoverlay=mcp2515-can0' in i: connection = 'SPI0'
					elif 'dtoverlay=mcp2515-can1' in i: connection = 'SPI1'
					if 'oscillator' in i:
						oList = i.split('=')
						oscillator = oList[1]
					if 'interrupt' in i:
						iList = i.split('=')
						interrupt = iList[1]
				interface = self.getInterface(connection)
				if 'pipedProviders' in data:
					for i in data['pipedProviders']:
						if i['pipeElements'][0]['options']['subOptions']['type']=='canbus-canboatjs':
							if interface == i['pipeElements'][0]['options']['subOptions']['interface']: 
								skId = i['id']
								enabled = i['enabled']
				self.listMcp2515.Append([connection,oscillator,interrupt,interface,skId])
				if skId and enabled: self.listMcp2515.SetItemBackgroundColour(self.listMcp2515.GetItemCount()-1,(0,191,255))
		file.close()

		if 'pipedProviders' in data:
			for i in data['pipedProviders']:
				if i['pipeElements'][0]['options']['subOptions']['type']=='canbus-canboatjs' and not 'canable' in i['pipeElements'][0]['options']['subOptions']['interface']:
					interface = i['pipeElements'][0]['options']['subOptions']['interface']
					skId = i['id']
					exists = False
					for ii in range(self.listMcp2515.GetItemCount()):
						if interface == self.listMcp2515.GetItemText(ii, 3): exists = True
					if not exists: self.listMcp2515.Append(['','','',interface,skId])

		self.toolbar3.EnableTool(301,False)
		self.toolbar3.EnableTool(304,False)
		self.SetStatusText('')

	def getInterface(self,connection):
		output = ''
		result = ''
		try:
			if connection == 'SPI0':
				output = subprocess.check_output('dmesg | grep -i "mcp251x spi0.0"', shell=True).decode()
			elif connection == 'SPI1':
				output = subprocess.check_output('dmesg | grep -i "mcp251x spi0.1"', shell=True).decode()
		except:pass
		if output:
			output = output.split(':')
			output = output[0].split(' ')
			for ii in output:
				if 'can' in ii: result = ii
		return result

	def onListlistMcp2515Selected(self,e):
		selected = self.listMcp2515.GetFirstSelected()
		if selected == -1: return
		self.toolbar3.EnableTool(304,True)
		skId = self.listMcp2515.GetItemText(selected, 4)
		connection = self.listMcp2515.GetItemText(selected, 0)
		if skId: self.toolbar3.EnableTool(301,True)
		else: self.toolbar3.EnableTool(301,False)
		if connection: self.toolbar3.EnableTool(304,True)
		else: self.toolbar3.EnableTool(304,False)

	def onListlistMcp2515Deselected(self,e):
		self.toolbar3.EnableTool(301,False)
		self.toolbar3.EnableTool(304,False)

	def onEditMcp2515SkCon(self,e):
		selected = self.listMcp2515.GetFirstSelected()
		if selected == -1: return
		skId = self.listMcp2515.GetItemText(selected, 4)
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/'+skId
		webbrowser.open(url, new=2)

	def onRefreshMcp2515(self,e):
		self.readMcp2515()

	def onRemoveMcp2515(self,e):
		selected = self.listMcp2515.GetFirstSelected()
		if selected == -1: return
		canConnection = self.listMcp2515.GetItemText(selected, 0)
		canOscillator = self.listMcp2515.GetItemText(selected, 1)
		canInterrupt = self.listMcp2515.GetItemText(selected, 2)
		interfaces = 0
		for i in range(self.listMcp2515.GetItemCount()):
			if self.listMcp2515.GetItemText(i, 0): interfaces = interfaces + 1
		interfaces = interfaces - 1
		if interfaces < 1: interfaces = ''
		else: interfaces = str(interfaces)
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/mcp2515.py', 'disable', canConnection, canOscillator, canInterrupt, interfaces])
		self.readMcp2515()
		self.ShowStatusBarYELLOW(_('Changes will be applied after restarting'))

	def onAddMcp2515(self,e):
		dlg = addMcp2515()
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			canConnection = dlg.canConnection.GetStringSelection()
			canOscillator = dlg.canOscillator.GetStringSelection()
			canInterrupt = dlg.canInterrupt.GetValue()
			if not canConnection or not canOscillator or not canInterrupt:
				self.ShowStatusBarRED(_('Fill in all fields'))
				dlg.Destroy()
				return
			interfaces = 0
			for i in range(self.listMcp2515.GetItemCount()):
				if self.listMcp2515.GetItemText(i, 0): interfaces = interfaces +1
				if self.listMcp2515.GetItemText(i, 0) == canConnection:
					self.ShowStatusBarRED(_('This connection already exists'))
					dlg.Destroy()
					return
				if self.listMcp2515.GetItemText(i, 2) == canInterrupt:
					self.ShowStatusBarRED(_('This interrupt GPIO already exists'))
					dlg.Destroy()
					return
			interfaces = interfaces + 1
			if interfaces < 1: interfaces = ''
			else: interfaces = str(interfaces)
			subprocess.call([self.platform.admin, 'python3', self.currentdir+'/mcp2515.py', 'enable', canConnection, canOscillator, canInterrupt, interfaces])
		dlg.Destroy()
		self.readMcp2515()
		self.ShowStatusBarYELLOW(_('Changes will be applied after restarting'))

################################################################################

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent, width,height):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=(width, height))
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class openPGNs(wx.Dialog):

	def __init__(self,parent,alias,bauds):
		self.error = ''
		self.can_device = alias
		self.baud_ = bauds
		self.parent = parent
		self.conf = parent.conf
		self.currentpath = parent.currentdir
		self.ttimer = 100
		Buf_ = bytearray(128)
		self.Buffer = bytearray(Buf_)
		self.Zustand=6
		self.buffer=0
		self.PGN_list=[]
		self.list_N2K_txt=[]
		self.list_count=[]
		self.p=0

		wx.Dialog.__init__(self, None, title=_('Open device PGNs'), size=(650,430))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timer_act, self.timer)

		panel = wx.Panel(self, 100)
		self.list_N2K = CheckListCtrl(panel, -1,240)
		self.list_N2K.SetBackgroundColour((230,230,230))
		self.list_N2K.SetPosition((10, 25))
		self.list_N2K.InsertColumn(0, _('TX PGN'), width=100)
		self.list_N2K.InsertColumn(1, _('info'), width=220)
		self.txLabel = wx.StaticText(panel, wx.ID_ANY, style=wx.ALIGN_CENTER)
		self.printing = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1,50))
		self.printing.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))

		apply_b = wx.Button(panel, label=_('Apply'))
		self.Bind(wx.EVT_BUTTON, self.apply, apply_b)
		close_b = wx.Button(panel, label=_('Close'))
		self.Bind(wx.EVT_BUTTON, self.OnClose, close_b)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddStretchSpacer(1)
		hbox.Add(apply_b, 0, wx.LEFT, 10)
		hbox.Add(close_b, 0, wx.LEFT, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.list_N2K, 1, wx.ALL | wx.EXPAND, 10)
		vbox.Add(self.txLabel, 0, wx.LEFT, 10)
		vbox.Add(self.printing, 1, wx.ALL | wx.EXPAND, 10)
		vbox.Add(hbox, 1, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(vbox)
		self.Centre()

		try:
			self.ser = serial.Serial(self.can_device, self.baud_, timeout=0.5)
		except:
			self.printing.SetValue(_('Error connecting with device ')+self.can_device)
			apply_b.Disable()
			self.list_N2K.Disable()
		else:
			self.read_N2K()
			self.check(0)
			self.timer.Start(self.ttimer)

	def check(self,e):
		self.printing.SetValue('')
		i=0
		self.work = True
		while (self.work):
			self.getCharfromSerial()
			time.sleep(0.01)
			i+=1
			if i>20:
				self.work = False

		self.Send_Command(1, 0x01, 0)
		time.sleep(0.2)

		counter=0
		for ii in self.list_N2K_txt:
			self.list_N2K.CheckItem(counter,False)
			counter+=1

		self.PGN_list=[]
		self.work = True
		self.Send_Command(1, 0x49, 0)
		i=0
		while (self.work):
			self.getCharfromSerial()
			time.sleep(0.01)
			i+=1
			if i>200:
				self.work = False
		self.read_stick_check()
		if len(self.PGN_list)<1: self.printing.SetValue(_('The list of enabled PGNs is empty, you may need to try a different baudrate or reset your device to 115200 bauds'))

	def apply(self,e):
		new = _('open PGNs: ')
		close = _('close PGNs: ')
		msg = ''
		counter = 0
		maxpgns = False
		st=''
		for ii in self.list_N2K_txt:
			if self.list_N2K.IsChecked(counter):
				exist=0
				for jj in self.PGN_list:
					if ii[0]==str(jj):
						exist=1
				if exist==0:
					st+=ii[0]+' '
					if len(self.PGN_list)<30:
						self.sendTX_PGN(int(ii[0]),1)
						self.PGN_list.append(ii[0])
						time.sleep(0.2)
					else: maxpgns = True
			counter+=1
		new += st

		st=''
		for jj in self.PGN_list:
			counter=0
			for ii in self.list_N2K_txt:
				exist=0
				if ii[0]==str(jj):
					if not self.list_N2K.IsChecked(counter):
						exist=1
					if exist==1:
						st+=ii[0]+' '
						self.sendTX_PGN(int(ii[0]),0)
						time.sleep(0.2)
				counter+=1
		close += st

		self.Send_Command(1, 0x01, 0)
		if maxpgns: msg += _('You can not activate more than 30 PGNs\n\n')
		msg += new+'\n'+close
		wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)
		self.check(0)

	def sendTX_PGN(self,lPGN,add):
		if add:
			data_ = (0,0,0,0,1,0xFE,0xFF,0xFF,0xFF,0xFE,0xFF,0xFF,0xFF)
			data = bytearray(data_)
		else:
			data = bytearray(13)
		data[0]=lPGN&255
		data[1]=(lPGN >> 8)&255
		data[2]=(lPGN >> 16)&255

		self.Send_Command(14, 0x47, data)

	def Send_Command(self, length, command, arg):
		data = bytearray(length+3)
		
		data[0] = 0xa1 #command
		data[1] = length #Actisense length
		data[2] = command
		i=3
		while i<length+2:
			data[i] = arg[i-3]
			i+=1
		self.SendCommandtoSerial(data)

	def timer_act(self,e):
		self.getCharfromSerial()

	def OnClose(self, event):
		self.timer.Stop()
		self.EndModal(wx.OK)

	def SendCommandtoSerial(self, TXs):
		crc = 0
		i = 0
		while i < TXs[1] + 2:
			crc += TXs[i]
			i += 1
		crc = (256 - crc) & 255
		TXs[TXs[1] + 2] = crc

		TYs = b''
		while i < TXs[1] + 3:
			TYs = TYs+bytes(TXs[i])
			if TXs[i] == 0x10:
				TYs = TYs+bytes(TXs[i])
			i += 1		
		start = b'\x10\x02'
		ende = b'\x10\x03'
		self.ser.write(start+TXs+ende)

	def getCharfromSerial(self):
		bytesToRead = self.ser.inWaiting()
		if bytesToRead>0:
			buffer=self.ser.read(bytesToRead)
			for i in buffer:
				self.parse(i)			

	def parse(self, b):
		if self.Zustand == 6: # zu Beginn auf 0x10 warten
			if b == 0x10:
				self.Zustand = 0x10
		elif self.Zustand == 0x10:
			if b == 0x10: # 0x10 Schreiben wenn zweimal hintereinander
				self.Buffer[self.p] = b
				self.p += 1
				self.Zustand = 0
			elif b == 0x02: # Anfang gefunden
				self.p = 0
				self.Zustand = 0
			elif b == 0x03: # Ende gefunden
				if self.crcCheck():
					self.output()
				self.p = 0
				self.Zustand = 6 # Auf Anfang zuruecksetzen
		elif self.Zustand == 0:
			if b == 0x10:
				self.Zustand = 0x10
			else:
				self.Buffer[self.p] = b
				self.p += 1

	def crcCheck(self):
		crc = 0
		i = 0
		while i < self.p:
			crc =(crc+ self.Buffer[i]) & 255
			i += 1
		return (crc == 0)

	def output(self):
		if self.Buffer[0] == 0x93 and self.Buffer[1] == self.p - 3:
			pass
		else:
			if self.Buffer[2] == 0x49 and self.Buffer[3] == 0x01:
				j = 0
				st=''
				self.PGN_list=[]
				while j < self.Buffer[14]:
					i=j*4
					lPGN=self.Buffer[15+i]+self.Buffer[16+i]*256+self.Buffer[17+i]*256*256
					if lPGN in self.PGN_list:
						print(lPGN,'already exists')
					else:
						self.PGN_list.append(lPGN)
						st+=str(lPGN)+' '

					j+=1
				self.printing.SetValue(st)
				self.txLabel.SetLabel(str(j)+_(" enabled transmission PGNs (max. 30):"))
				self.work = False

	def read_N2K(self):
		if self.list_N2K.GetItemCount()<3:
			while self.list_N2K.GetItemCount()>3:
				self.list_N2K.DeleteItem(self.list_N2K.GetItemCount()-1)

			self.list_N2K_txt=[]
			with open(self.currentpath+'/data/N2K_PGN.csv') as f:
				self.list_N2K_txt = [x.strip('\n\r').split(',') for x in f.readlines()]

			for ii in self.list_N2K_txt:
				pgn=int(ii[0])
				self.list_N2K.Append([pgn,ii[1]])

	def read_stick_check(self):
		counter=0
		self.list_N2K.CheckItem(0,False)
		for ii in self.list_N2K_txt:
			for jj in self.PGN_list:
				if ii[0]==str(jj):
					self.list_N2K.CheckItem(counter)
			counter+=1
		self.list_N2K.Update()

################################################################################

class addMcp2515(wx.Dialog):
	def __init__(self):
		title = _('Add MCP2515 device')

		wx.Dialog.__init__(self, None, title=title, size=(300, 260))
		panel = wx.Panel(self)

		canConnectionLabel = wx.StaticText(panel, label=_('Connection'))
		self.canConnection = wx.Choice(panel, choices=('SPI0', 'SPI1'), style=wx.CB_READONLY)


		canOscillatorLabel = wx.StaticText(panel, label=_('Oscillator'))
		self.canOscillator = wx.Choice(panel, choices=('8000000', '16000000'), style=wx.CB_READONLY)


		canInterruptLabel = wx.StaticText(panel, label=_('Interrupt GPIO'))
		self.canInterrupt = wx.TextCtrl(panel)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(canConnectionLabel, 0, wx.LEFT | wx.EXPAND, 10)
		hbox1.Add(self.canConnection, 1, wx.LEFT |  wx.RIGHT | wx.EXPAND, 10)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(canOscillatorLabel, 0, wx.LEFT | wx.EXPAND, 10)
		hbox2.Add(self.canOscillator, 1, wx.LEFT |  wx.RIGHT | wx.EXPAND, 10)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(canInterruptLabel, 0, wx.LEFT | wx.EXPAND, 10)
		hbox3.Add(self.canInterrupt, 1, wx.LEFT |  wx.RIGHT | wx.EXPAND, 10)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddStretchSpacer(1)
		hbox.Add(cancelBtn, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
		hbox.Add(okBtn, 0, wx.RIGHT | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(10)
		vbox.Add(hbox1, 0, wx.EXPAND, 0)
		vbox.AddSpacer(10)
		vbox.Add(hbox2, 0, wx.EXPAND, 0)
		vbox.AddSpacer(10)
		vbox.Add(hbox3, 0, wx.EXPAND, 0)
		vbox.AddStretchSpacer(1)
		vbox.Add(hbox, 0, wx.EXPAND, 0)
		vbox.AddSpacer(10)

		panel.SetSizer(vbox)
		self.panel = panel

		self.Centre() 

	def OnDelete(self,e):
		self.EndModal(wx.ID_DELETE)

################################################################################

class AddPort(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, title=_('Add Serial Port'), size=(-1,200))
		panel = wx.Panel(self)

		ports = serial.tools.list_ports.comports(True)
		self.listDevices = []
		for port in ports:
			self.listDevices.append(port.device)

		OPserial = False
		self.listDevicesOP = []
		
		for device in self.listDevices:
			if 'ttyOP' in device:
				self.listDevicesOP.append(device)
				OPserial = True

		if OPserial:
			self.port = wx.Choice(panel, choices=self.listDevicesOP)
			self.OPserialTrue = wx.CheckBox(panel, label=_('Show only Openplotter-Serial managed ports'))
			self.OPserialTrue.Bind(wx.EVT_CHECKBOX, self.on_OPserialTrue)
			self.OPserialTrue.SetValue(True)
		else:
			self.port = wx.Choice(panel, choices=self.listDevices)
		
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(cancelBtn, 1, wx.ALL | wx.EXPAND, 10)
		hbox.Add(okBtn, 1, wx.ALL | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.port, 0, wx.ALL | wx.EXPAND, 10)
		if OPserial:
			vbox.Add(self.OPserialTrue, 0, wx.ALL | wx.EXPAND, 10)
		vbox.AddStretchSpacer(1)
		vbox.Add(hbox, 0, wx.EXPAND, 0)
		
		panel.SetSizer(vbox)
		self.Centre()
		
	def on_OPserialTrue(self,e):
		self.port.Clear()
		if self.OPserialTrue.GetValue():
			self.port.AppendItems(self.listDevicesOP)
		else:
			self.port.AppendItems(self.listDevices)			

################################################################################

def main():
	app = wx.App()
	MyFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
