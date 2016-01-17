from FileManagement import FMFileManagement
from FileManagementPreferences import *

import os

class FMLastFilesFile:
	
	@staticmethod
	def open(filepath=None):
		print "TODO : depricated !!!!"
		if filepath==None:
			filepath = os.path.expanduser(
									FMPreferences['LAST_FILES_FILE_PATH'])
			if not os.path.isabs(filepath):
				filepath=os.path.join(FMPreferences.abs_path_script_file,filepath)
		res=[]
		if os.path.exists(filepath):
			# We read the config.txt file
			file=FMFileManagement.open(filepath,output='readlines')

			# We fill the self.result_dictionary with the values contained into the file
			for ligne in file:
				ligne=ligne.strip()
				if len(ligne)>=0:
					res.append(ligne)
		return res
		
	@staticmethod
	def save(list_files,filepath=None):
		if filepath==None:
			filepath = os.path.expanduser(
									FMPreferences['LAST_FILES_FILE_PATH'])
			if not os.path.isabs(filepath):
				filepath=os.path.join(FMPreferences.abs_path_script_file,filepath)
		
		text = "\n".join(list_files)
		return FMFileManagement.save(text,filepath)
		
