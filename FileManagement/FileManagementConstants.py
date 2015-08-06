import os
############ IMPORTATION OF CMConstantsAbstarct ############
try :
	# We try to see if it is already available
	from ConstantsManagement.ConstantsManagementConstantsAbstarct import \
			CMConstantsAbstarct
except ImportError:
	# Otherwise we try to see if it is not in the parent directory (but if is 
	# has been loaded before, it would not be reloaded anymore.
	import imp
		
	dir,f	= os.path.split(__file__)
	dir,f	= os.path.split(dir)
	dir 	= os.path.join(dir,'ConstantsManagement')

	foo = imp.find_module('ConstantsManagementConstantsAbstarct', [dir])
	foo = imp.load_module('ConstantsManagementConstantsAbstarct',*foo)
	CMConstantsAbstarct=foo.CMConstantsAbstarct
############################################################

class FMConstantsAbstarct (CMConstantsAbstarct):
	all_constants=  dict(	
			AUROCORRECTION_FILE_PATH	= (unicode	,
					"~/.athena/autocorrection.txt"	,
					"The path to the auto-correction file"),
			LAST_FILES_FILE_PATH		= (unicode	,
					"~/.athena/last_files.txt",
					"The path to the last-opened-files file"),
			MAX_FILES_NUMBER		= (int	,
					1000,
					"When saving a file, to avoid a erase another file, it "+\
					"adds a number at the end of the name bewteen 0 and "+\
					"MAX_FILES_NUMBER"),
			
			)
FMConstants=FMConstantsAbstarct()
