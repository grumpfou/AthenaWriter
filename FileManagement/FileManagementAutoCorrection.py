from .FileManagement import FMFileManagement
from .FileManagementPreferences import *

class FMAutoCorrectionFile:
	
	@staticmethod
	def open(filepath=None):
		print("TODO : depricated !!!!")
		if filepath==None:
			filepath = os.path.expanduser(
									FMConstants['AUROCORRECTION_FILE_PATH'])
			if not os.path.isabs(filepath):
				filepath=os.path.join(FMConstants.abs_path_script_file,filepath)
			
		res={}
		if os.path.exists(filepath):		
			# We read the config.txt file
			file=FMFileManagement.open(filepath,output='readlines')

			# We fill the self.result_dictionary with the values contained into the file
			for ligne in file:
				ligne=ligne.strip()
				i=ligne.find(' ')
				if i!= -1:
					k=ligne[:i]
					v=ligne[i:].strip()
					res[k]=v
		return res
