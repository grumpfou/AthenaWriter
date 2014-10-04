from LastFilesConstants import LFConstants

import os

class LFList:
	def __init__(self,list_files=None):
		if list_files==None: list_files=[]
		self.list_files=list_files
		
		if LFConstants['SKIP_NON_EXISTING']:
			self.check_existing()
			
	def addFile(self,file):
		file=os.path.abspath(file)
		if file in self.list_files:
			self.list_files.remove(file)
		self.list_files.insert(0,file)
		if LFConstants['SKIP_NON_EXISTING']:
			self.check_existing()
		if len(self.list_files)>= LFConstants['LENGTH_FILES_LIST']:
			self.list_files=self.list_files[:LFConstants['LENGTH_FILES_LIST']]
		
	def check_existing(self):
		for i in (range(len(self.list_files)))[::-1]:
			if not os.path.exists(self.list_files[i]):
				self.list_files.pop(i)
	
