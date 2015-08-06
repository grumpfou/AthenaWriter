import os
############ IMPORTATION OF CMConstantsAbstarct ############
try :
	# We try to see if it is already available
	from ConstantsManagement.ConstantsManagementConstantsAbstarct import CMConstantsAbstarct
except ImportError:
	# Otherwise we try to see if it is not in the parent directory (but if is has been loaded before,
	# it would not be reloaded anymore.
	import imp
		
	dir,f	= os.path.split(__file__)
	dir,f	= os.path.split(dir)
	dir 	= os.path.join(dir,'ConstantsManagement')

	foo = imp.find_module('ConstantsManagementConstantsAbstarct', [dir])
	foo = imp.load_module('ConstantsManagementConstantsAbstarct',*foo)
	CMConstantsAbstarct=foo.CMConstantsAbstarct
############################################################

class CLConstantsAbstarct (CMConstantsAbstarct):
	all_constants=  dict(	
				GLOBAL_DIR  = (unicode,'./config/','The dirpath to the general configurtion files (relative to the file AthenaWriterCore.py'),
				USER_DIR	 = (unicode,'~/.athena/','The absolute dirpath to the user configuration files'),
				LOCAL_DIR	 = (unicode,'.','The local dirpath to the user configuration files relative to the oppened file'),
				LAST_FILE_LENGTH	= (int	,10		,"The number of files to keep in memory."),
				LAST_FILE_SKIP_NON_EXISTING	= (bool	,False	,"If true, check if each file is existing."),
				)
CLConstants = CLConstantsAbstarct()
