from ConstantsManagement.ConstantsManagementConstantsAbstarct import *


from TextEdit.TextEditConstants 			import TEConstants
from DocStatistics.DocStatisticsConstants	import DSConstants
from FileManagement.FileManagementConstants import FMConstants
from LastFiles.LastFilesConstants 			import LFConstants
from FileImport.FileImportConstants 		import FIConstants
from FileExport.FileExportConstants 		import FEConstants
from TextStyles.TextStylesConstants 		import TSConstants
from MetaData.MetaDataConstants 			import MDConstants



from FileManagement.FileManagementFileConstants import FMFileConstants


import os
import sys

path_to_config_file_general = os.path.join(
		CMConstantsAbstarct().abs_path_script_file,
		'./config/config.txt'
		)
path_to_config_file_user = '~/.athena/config_AthenaWriter.txt'

class AWAllConstants (CMConstantsAbstarct):
	all_constants 			= {
			# 'TEXT_SIZE'			 :(int,20,		  "Size of the text in the "+\
					# "TextEdit"),
			'TEXT_INDENT'		 :(int,50,        "Indentation width of the "+\
					"text in the TextEdit"),
			# 'TEXT_FONT'			 :(str,'Times',   "Name of the Font in the "+\
					# "TextEdit"),
			'TEXT_LINE_HEIGHT'	 :(int,100,       "Height of the interline "+\
					"in the TextEdit"),
			# 'TEXT_ALIGNMENT'	 :(str,'justify', "Alignment in the "+\
					# "TextEdit ('justify', 'right', 'left' or 'center')"),
			'TEXT_MARGIN'		 :(float,50,	  "Margin of the text edit"),
			'DLT_OPEN_SAVE_SITE' :(unicode,'~',   "Default directory when "+\
				"opening or saving as"),
			'INIT_SIZE_X'		 :(int,750,	  	  "Length of the main window"),
			'INIT_SIZE_Y'		 :(int,500,	 	  "Height of the main window"),
			'TIME_STATUS_MESSAGE':(int,3000, 	  "Time it leaves a message "+\
				"into the status bar (put 0 if it is indefinitely)"),
			'TMP_FILE_MARK'		 :(str,'~', 	  "The mark to put in front "+\
				"of the temporary files' name"),
			'AUTOSAVE' 	 		 :(bool,False, 	  "Allow or not the autosave"),
			'AUTOSAVE_TEMPO' 	 :(float,300., 	  "Time in seconds between "+\
				"each autosave"),
			'EXTERNAL_SOFT_PATH' :(str,"", 	      "Path to the external "+\
				"software where to send the file."),
			'DO_METADATA'        :(bool,True,	  "Is True if you want to "+\
				"save the meta-data file, while saving each file."),
			'FULLSCREEN_CENTRAL_MAX_SIZE'   :(int,-1, "Maximum size for the "+\
				"central widget in fullscreen (if negative, no limit)"),
			}
	all_sub_constants = {
						'TextEdit'			: TEConstants	,
						'DocStatistics' 	: DSConstants	,
						'FileManagement' 	: FMConstants 	,
						'LastFiles'		 	: LFConstants 	,
						'FileImport'	 	: FIConstants 	,
						'FileExport'	 	: FEConstants 	,
						'TextStyles'	 	: TSConstants 	,
						'MetaData'		 	: MDConstants 	,
						}
						
	def __init__(self,file_to_read=None):
		CMConstantsAbstarct.__init__(self)
		self.file_to_read = file_to_read
	# 	
	# 	self.file_to_read = file_to_read
	# 	# if type(file_to_read)!=str or type(file_to_read)!=unicode:
	# 	if file_to_read == None:
	# 		# file_to_read=path_to_config_file :
	# 		file_to_read=os.path.join(CMConstantsAbstarct().abs_path_script_file,path_to_config_file)
	# 			
	# 	self.loadFile(file_to_read)
				
			
			
	# def loadFile(self,file_to_read=None):
		# """Load the constants from the file file_to_read. If file_to_read is 
		# None, then it will take self.file_to_read if it exists.
		# """
		# if file_to_read==None:	
			# file_to_read = self.file_to_read
			
		# if file_to_read!=False:
			# file_to_read = os.path.expanduser(file_to_read)
			# if os.path.exists(file_to_read):
				# self.file_to_read = file_to_read
				# result_dictionary = FMFileConstants.open(self.file_to_read)
				# for k,v in result_dictionary.items():
					# try:
						# self.__setitem__(k,v)
					# except  KeyError,e:
						# print "Caution : ",e
			# else:
				# print (file_to_read+' not found, taking the default options!')
				# CMConstantsAbstarct.__init__(self)
				
		# else:
			# raise Exception('file_to_read was not specified')				
	
	# def saveFile(self,file_to_read=None):
		# """Save the constants in the file file_to_read. If file_to_read is 
		# None, then it will take self.file_to_read if it exists.
		# """		
		# if file_to_read==None:	
			# file_to_read = self.file_to_read
		
		# if file_to_read:
			# FMFileConstants.save(self.to_string(),file_to_read)
		# else:
			# raise Exception('file_to_read was not specified')

AWConstants = AWAllConstants()
AWConstants.loadFile(file_manager = FMFileConstants,
									file_to_read = path_to_config_file_general)
AWConstants.loadFile(file_manager = FMFileConstants,
									file_to_read = path_to_config_file_user)

