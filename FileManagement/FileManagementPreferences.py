############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from ConstantsManager.ConstantsManager import CMConstantsManager
															

class FMPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(
		AUROCORRECTION_FILE_PATH = (str ,"~/.athena/autocorrection.txt"),
		LAST_FILES_FILE_PATH = (str	,"~/.athena/last_files.txt"),
		MAX_FILES_NUMBER	 = (int,1000,),
			
			)
			
	descriptions 	= dict(		
		AUROCORRECTION_FILE_PATH	= "The path to the auto-correction file",
		LAST_FILES_FILE_PATH		= "The path to the last-opened-files file",
		MAX_FILES_NUMBER		= "When saving a file, to avoid a erase "+\
				"another file, it adds a number at the end of the name "+\
				"bewteen 0 and MAX_FILES_NUMBER",
				)
FMPreferences=FMPreferencesAbstarct()
