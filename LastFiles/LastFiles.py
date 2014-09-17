from LastFilesConstants import LFConstants

import os

class LFList:
	def __init__(self,list=None):
		if list==None: list=[]
		self.list=list
		
		if LFConstants['SKIP_NON_EXISTING']:
			self.check_existing()
			
	def addFile(self,file):
		file=os.path.abspath(file)
		if file in self.list:
			self.list.remove(file)
		self.list.insert(0,file)
		if LFConstants['SKIP_NON_EXISTING']:
			self.check_existing()
		if len(self.list)>= LFConstants['LENGTH_FILES_LIST']:
			self.list=self.list[:LFConstants['LENGTH_FILES_LIST']]
		
	def check_existing(self):
		for i in (range(len(self.list)))[::-1]:
			if not os.path.exists(self.list[i]):
				self.list.pop(i)
	
