from ConstantsManager.ConstantsManager import CMConstantsManager

from ConfigLoading.ConfigLoadingPreferences   import CLPreferences
from DocExport.DocExportPreferences			  import DEPreferences
from DocImport.DocImportPreferences			  import DIPreferences
from DocProperties.DocPropertiesPreferences	  import DPPreferences
from FileManagement.FileManagementPreferences import FMPreferences
from TextEdit.TextEditPreferences 			  import TEPreferences
from TextLanguages.TextLanguagesPreferences	  import TLPreferences
from TextStyles.TextStylesPreferences	  	  import TSPreferences


from ConfigLoading.ConfigLoading import CLPreferencesFiles
from CommonObjects.CommonObjects import COOrderedDict



import os
import sys

class AWPreferencesAbstract (CMConstantsManager):
	start_defaults 	= dict(
			DLT_OPEN_SAVE_SITE 			= (unicode,'~'),
			INIT_SIZE_X		 			= (int,750),
			INIT_SIZE_Y		 			= (int,500),
			TIME_STATUS_MESSAGE			= (int,3000),
			TMP_FILE_MARK		 			= (str,'~'),
			AUTOSAVE 	 		 			= (bool,False),
			AUTOSAVE_TEMPO 	 			= (float,300.),
			EXTERNAL_SOFT_PATH 			= (str,""),
			FULLSCREEN_CENTRAL_MAX_SIZE   = (int,-1),
			NOT_USED					= (int,10),
			)
			

			
	descriptions 	= dict(
			DLT_OPEN_SAVE_SITE ="Default directory when opening or saving as",
			INIT_SIZE_X		 ="Length of the main window",
			INIT_SIZE_Y		 ="Height of the main window",
			TIME_STATUS_MESSAGE="Time it leaves a message into the status "+\
					"bar (put 0 if it is indefinitely)",
			TMP_FILE_MARK		 ="The mark to put in front of the "+\
					"temporary files' name",
			AUTOSAVE 	 		 ="Allow or not the autosave",
			AUTOSAVE_TEMPO 	 ="Time in seconds between each autosave",
			EXTERNAL_SOFT_PATH ="Path to the external software where to "+\
					"send the file.",
			FULLSCREEN_CENTRAL_MAX_SIZE   = "Maximum size for the central "+\
					"widget in fullscreen (if negative, no limit)",
			NOT_USED = "A constants only used for debugging, not used in "+\
					"software...",
			)

AWPreferences = AWPreferencesAbstract()

class Class(dict):
	def __init__(self,a):
		if type(a)==dict:
			self.list_keys = a.keys()
		elif type(a)==list:
			self.list_keys = [v[0] for v in a]
		dict.__init__(self,a)
		
	def keys(self):
		return self.list_keys
		
	def items(self):
		for k in self.keys():
			return k,self[k]
	
	
	
AWDictPreferences = COOrderedDict([
						('General'			, AWPreferences),
						('ConfigLoading'	, CLPreferences),
						('DocExport'		, DEPreferences),
						('DocImport'		, DIPreferences),
						('DocProperties'	, DPPreferences),
						('FileManagement'	, FMPreferences),
						('TextEdit'			, TEPreferences),
						('TextLaguages'		, TLPreferences),
						('TextStyles'		, TSPreferences),
						])
	 
					
def AWOverwritePreferences(d):
	over = {k:{} for k in AWDictPreferences.keys()}
	for k,v in d.items():
		if not '.' in k: # TODO raise an error if not
			print "WARNING : no '.' in the key ",k
		else:
			kk = k[:k.find('.')]
			kkk = k[k.find('.')+1:]
			if kk not in over.keys(): # TODO raise an error if not
				print "WARNING: unkown key ",kk
			else:
					over[kk][kkk] = v 
	for k,v in over.items():
		try :
			AWDictPreferences[k].update(v)
		except KeyError,e:
			print "WARNING: for key",k,':',str(e)
		
					
def AWPreferencesToDict(skip_same_as_dft=False):
	"""
	Will return the dict from all the preferences of the software under the
	form of: {Preferences.foo = value ,...}
	- skip_same_as_dft: if true, skip the same as default preferences
	
	returns:
	- pref_dict: dict that contains the preferences
	- descr_dict: dict that contains the descriptions of the preferences
	"""
	pref_dict = {}
	descr_dict = {}
	for k,v in AWDictPreferences.items():
		for kk,vv in v.items(skip_same_as_dft=skip_same_as_dft):
			kkk = k+'.'+kk
			pref_dict[kkk] = vv
			if v.descriptions.has_key(kk):
				descr_dict[kkk] = v.descriptions[kk]
	return pref_dict , descr_dict
		
	
d = CLPreferencesFiles.get_values(errors='print')
AWOverwritePreferences(d)

