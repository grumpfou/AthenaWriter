############################# LIBRARIES AVAILABLE #############################
import os,sys,subprocess
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

def DITestLibreOffice():
	try :
		return subprocess.check_call(
				[DIPreferences['LIBREOFFICE_COMMAND'],'--version'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)==0
	except OSError:
		return False
