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
class TSAllConstants (CMConstantsAbstarct):
	all_constants= {
			'NB_CHAR_PER_LINE'  :(int,56,		  "Number maximum of char in a line of a book"),
			'NB_LINE_PER_PAGE'  :(int,35,		  "Number of line in a page of a book"),
			'NB_CHAR_PER_INDENT':(int,3,		  "Number of spaces that represent the indent"),
			}
	
TSConstants=TSAllConstants()
