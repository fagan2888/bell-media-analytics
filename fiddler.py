## This file contains tools to start and close fiddler, as well as to export and clear the sessions in fiddler, and set filters
import pywinauto, auth
from pywinauto import application
from time import sleep, localtime, strftime

f = application.Application()

class fiddlerClass:

	def start_fiddler(self):
		"""Starts Fiddler2"""
		f.start(auth.fiddler_exe)
		sleep(10)
		w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]
		window = f.window_(handle=w_handle)
		print "Fiddler has been started!"

	def maximize(self):
		"""Maximizes Fiddler2."""
		w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]#, class_name='WindowsForms10.Window.8.app.0.33c0d9d')[0]
		window = f.window_(handle=w_handle)
		window.Maximize()

	def set_focus(self):
		"""Attempts to bring Fiddler2 to the foreground."""
		print "Attempting to make Fiddler2 the active window."
		w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]#, class_name='WindowsForms10.Window.8.app.0.33c0d9d')[0]
		window = f.window_(handle=w_handle)
		window.SetFocus()

	def export_all_sessions(self, name):
		"""Exports all sessions to whatever location you pass in as a HAR file. Note: Fiddler2 needs to be the active application for this to work."""
		try:
			#self.set_focus()
			sleep(1)
			w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]
			window = f.window_(handle=w_handle)
			window.MenuItem(u'&File->&Export Sessions->&All Sessions...').Click()
			sleep(1)
			w_handle = pywinauto.findwindows.find_windows(title=u'Select Export Format')[0]
			window = f.window_(handle=w_handle)
		
			# Here, make sure it's the HAR type
			ctrl = window['0']
			ctrl.Click() # what
			ctrl.Select('HTTPArchive v1.2')
			# Done making sure it's the HAR type
			ctrl = window['&Next']
			ctrl.Click()
			sleep(1)

			w_handle = pywinauto.findwindows.find_windows(title=u'Export As HTTPArchive v1.2')[0]
			window = f.window_(handle=w_handle)

			# Here, enter the path/name and save
			ctrl = window['ComboBox2']
			sleep(2)
			ctrl.TypeKeys(name, with_spaces = True)
			sleep(3)
			ctrl = window['&Save']
			ctrl.Click()
			sleep(2)
			print "All sessions have been exported!"
		except:
			print "There was nothing to export ... "

	def close_fiddler(self):
		"""Closes Fiddler2. Sometimes this doesn't work if Fiddler2 is not the active application."""
		try:
			#self.set_focus()
			sleep(1)
			w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]
			sleep(1)
			window = f.window_(handle=w_handle)
			sleep(1)
			window.Close()
			print "Fiddler has been closed!"
		except:
			print "Closing Fiddler failed!"

	def clear_all_sessions(self):
		"""Attempts to clear all sessions in Fiddlers."""
		try:
			#self.set_focus()
			sleep(1)
			w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]
			sleep(1)
			window = f.window_(handle=w_handle)
			window.MenuItem(u'&Edit').Click()
			window.MenuItem(u'&Edit->&Remove').Click()
			window.MenuItem(u'&Edit->&Remove->&All Sessions\tCtrl+X').Click()
			print "All sessions cleared!"
		except:
			print "There was probably nothing to clear in Fiddler ... (or something went wrong)"

	def set_filter_internal(self, ctrl, window):
		"""A helper for set_filter. Mostly exists for re-factoring purposes."""
		ctrl = window['Button14']
		if ctrl.IsEnabled() == False:
			# "Use filters" button
			ctrl = window['Button5']
			ctrl.Click()
			sleep(1)
			ctrl = window['Button14']
			ctrl.Click()
			sleep(1)
			ctrl = window['Edit7']
			ctrl.TypeKeys("b/ss")
			print "Filters have been set!!"
		else:
			print "Filters were already set!"


	def set_filter(self):
		"""Sets filters to only read analytics data from company sites if filters are not already set. Otherwise, it does nothing."""
		try:
			sleep(1)
			#self.set_focus()
			sleep(3)
			w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]
			window = f.window_(handle=w_handle)
			ctrl = window['TabControl']
			ctrl.Click()
			# Selecting "Filters" from the possible tabs # may need to change this if FiddlerScript is installed?
			ctrl.Select(5)  # was 5 testing
			self.set_filter_internal(ctrl, window)
			## Now, we repeat because Fiddler is not consistent in numbering tabs.
			w_handle = pywinauto.findwindows.find_windows(title=u'Fiddler Web Debugger')[0]
			window = f.window_(handle=w_handle)
			ctrl = window['TabControl']
			ctrl.Click()
			ctrl.Select(4)
			self.set_filter_internal(ctrl, window)
			sleep(1)
		except:
			print "Failed at setting filters in Fiddler!"

