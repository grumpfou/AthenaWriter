from ConfigLoadingPreferences import CLPreferences

import os

class CLLastFiles:
	def __init__(self,list_files=None):
		if list_files==None: list_files=[]
		self.list_files=list_files
		
		if CLPreferences['LAST_FILE_SKIP_NON_EXISTING']:
			self.check_existing()
			
	def addFile(self,file):
		file=os.path.abspath(file)
		if file in self.list_files:
			self.list_files.remove(file)
		self.list_files.insert(0,file)
		if CLPreferences['LAST_FILE_SKIP_NON_EXISTING']:
			self.check_existing()
		if len(self.list_files)>= CLPreferences['LAST_FILE_LENGTH']:
			self.list_files=self.list_files[:CLPreferences['LAST_FILE_LENGTH']]
		
	def check_existing(self):
		for i in (range(len(self.list_files)))[::-1]:
			if not os.path.exists(self.list_files[i]):
				self.list_files.pop(i)
	
