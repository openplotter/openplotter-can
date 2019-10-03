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
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(__file__)
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-can',self.currentLanguage)

		wx.Frame.__init__(self, None, title=_('OpenPlotter CAN'), size=(800,444))
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
		self.AddSkCon = self.toolbar1.AddTool(104, _('SK connections'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onAddSkCon, self.AddSkCon)
		self.SKtoN2K = self.toolbar1.AddTool(105, _('Output'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onSKtoN2K, self.SKtoN2K)
		self.toolbar1.AddSeparator()
		toolApply = self.toolbar1.AddTool(106, _('Apply'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolApply, toolApply)
		toolCancel = self.toolbar1.AddTool(107, _('Cancel'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolCancel, toolCancel)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.sk = wx.Panel(self.notebook)
		self.op = wx.Panel(self.notebook)
		self.mcp2515 = wx.Panel(self.notebook)
		self.notebook.AddPage(self.sk, _('CAN-USB'))
		self.notebook.AddPage(self.op, _('CAN-USB / CANable'))
		self.notebook.AddPage(self.mcp2515, _('MCP2515'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-24.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-24.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/chip.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		if self.platform.skPort: 
			self.toolbar1.EnableTool(104,True)
			if self.platform.isSKpluginInstalled('signalk-to-nmea2000'): self.toolbar1.EnableTool(105,True)
			else: self.toolbar1.EnableTool(105,False)
		else:
			self.toolbar1.EnableTool(104,False)
			self.toolbar1.EnableTool(105,False)

		self.pageSk()
		self.pageOp()
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
		self.SetStatusText('')
		if self.notebook.GetSelection() == 1 or self.notebook.GetSelection() == 2:
			self.toolbar1.EnableTool(106,True)
			self.toolbar1.EnableTool(107,True)
		else:
			self.toolbar1.EnableTool(106,False)
			self.toolbar1.EnableTool(107,False)

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/can/can_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def pageMcp2515(self):
		pass

	def pageSk(self):
		skLabel = wx.StaticText(self.sk, label='Actinsense NGT-1 (canboatjs)')
		self.listSKcan = wx.ListCtrl(self.sk, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listSKcan.InsertColumn(0, _('ID'), width=200)
		self.listSKcan.InsertColumn(1, _('Serial Port'), width=200)
		self.listSKcan.InsertColumn(2, _('Baud Rate'), width=200)
		self.listSKcan.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSKcanSelected)
		self.listSKcan.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSKcanDeselected)

		self.toolbar2 = wx.ToolBar(self.sk, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.editSkCon = self.toolbar2.AddTool(201, _('Edit Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onEditSkCon, self.editSkCon)
		self.RefreshSk = self.toolbar2.AddTool(202, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.onRefreshSk, self.RefreshSk)
		self.toolbar2.AddSeparator()
		self.SKcanTX = self.toolbar2.AddTool(203, _('Open TX PGNs'), wx.Bitmap(self.currentdir+"/data/openplotter-24.png"))
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
						self.sklist.append([i['id'],i['pipeElements'][0]['options']['subOptions']['device'],i['pipeElements'][0]['options']['subOptions']['baudrate'],i['enabled']])
		except:pass

		self.listSKcan.DeleteAllItems()
		for ii in self.sklist:
			self.listSKcan.Append([ii[0],ii[1],str(ii[2])])
			if ii[3]: self.listSKcan.SetItemBackgroundColour(self.listSKcan.GetItemCount()-1,(0,191,255))


	def onCanUsbSetup(self,e):
		subprocess.call(['pkill', '-15', 'CAN-USB-firmware'])
		subprocess.call(['x-terminal-emulator','-e', 'CAN-USB-firmware'])

	def onAddSkCon(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
		webbrowser.open(url, new=2)

	def onSKtoN2K(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea2000'
		webbrowser.open(url, new=2)

	def onEditSkCon(self,e):
		selected = self.listSKcan.GetFirstSelected()
		if selected == -1: return
		index = self.listSKcan.GetItem(selected, 0)
		skId = index.GetText()
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/'+skId
		webbrowser.open(url, new=2)

	def onRefreshSk(self,e):
		self.readSk()

	def onSKcanTX(self,e):
		pass

	def onListSKcanSelected(self,e):
		pass

	def onListSKcanDeselected(self,e):
		pass

	def pageOp(self):
		pass

	def OnSkConnections(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
		webbrowser.open(url, new=2)

	def OnSkTo0183(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea0183'
		webbrowser.open(url, new=2)

	def OnSkTo2000(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea2000'
		webbrowser.open(url, new=2)

	def OnToolApply(self,e):
		pass
		
	def OnToolCancel(self,e):
		pass

################################################################################



################################################################################

def main():
	app = wx.App()
	MyFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
