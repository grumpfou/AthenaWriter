from ConstantsManagement.ConstantsManagementConstantsAbstarct import *
from ConfigLoading.ConfigLoading import CLPreferences


from DocStatistics.DocStatisticsConstants	import DSConstants
from FileExport.FileExportConstants 		import FEConstants
from FileImport.FileImportConstants 		import FIConstants
from FileManagement.FileManagementConstants import FMConstants
from LastFiles.LastFilesConstants 			import LFConstants
from MetaData.MetaDataConstants 			import MDConstants
from TextEdit.TextEditConstants 			import TEConstants
from TextStyles.TextStylesConstants 		import TSConstants




import os
import sys


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
						

d = CLPreferences.get_values()
AWConstants = AWAllConstants(dict_overwrite=d)
if __name__ == '__main__':
	print AWConstants.to_string()
