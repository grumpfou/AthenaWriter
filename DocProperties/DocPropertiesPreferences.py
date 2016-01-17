############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from ConstantsManager.ConstantsManager import CMConstantsManager
															
class DPPreferencesAbstarct (CMConstantsManager):
			
	start_defaults 	= dict(
		NB_CHAR_PER_LINE   =(int,56),
		NB_LINE_PER_PAGE   =(int,35),
		NB_CHAR_PER_INDENT =(int,4),
		
		DEFAULT_AUTHOR		= (str,""),
			)
			
	descriptions 	= dict(	
		NB_CHAR_PER_LINE   = "Number maximum of char in a line of a book",
		NB_LINE_PER_PAGE   = "Number of line in a page of a book",
		NB_CHAR_PER_INDENT = "Number of spaces that represent the indent",
		DEFAULT_AUTHOR	   ="Default author when creating a new file" ,
		)
	
DPPreferences=DPPreferencesAbstarct()
