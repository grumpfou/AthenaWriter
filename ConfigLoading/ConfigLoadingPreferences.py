############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from ConstantsManager.ConstantsManager import CMConstantsManager


class CLPreferencesAbstarct (CMConstantsManager):
	start_defaults=  dict(	
		GLOBAL_DIR  				= (unicode,'./config/'),
		USER_DIR	 				= (unicode,'~/.athena/'),
		LOCAL_DIR	 				= (unicode,'.'),
		LAST_FILE_LENGTH			= (int,10),
		LAST_FILE_SKIP_NON_EXISTING	= (bool	,False),
				)
				
	descriptions=  dict(		
		GLOBAL_DIR  = 'The dirpath to the general configurtion files '+\
			'(relative to the file AthenaWriterCore.py',
		USER_DIR	 = 'The absolute dirpath to the user configuration files',
		LOCAL_DIR	 = 'The local dirpath to the user configuration files '+\
			'relative to the oppened file',
		LAST_FILE_LENGTH	= 'The number of files to keep in memory.',
		LAST_FILE_SKIP_NON_EXISTING	= 'If true, check if each file is '+\
			'existing.'
			
			
			)
CLPreferences = CLPreferencesAbstarct()
