############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from ConstantsManager.ConstantsManager import CMConstantsManager

class DIPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(	
				LIBREOFFICE_COMMAND	= (str	,'libreoffice'),
			)
			
	descriptions 	= dict(	
		LIBREOFFICE_COMMAND	= "The command to open libreoffice (in Linux, "+\
			"just 'libreoffice' should be enough",
			)
DIPreferences = DIPreferencesAbstarct()
