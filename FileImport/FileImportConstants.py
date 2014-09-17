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

class FIConstantsAbstarct (CMConstantsAbstarct):
	all_constants=  dict(	
				LIBREOFFICE_COMMAND	= (str	,'"C:\Program Files (x86)\LibreOffice 4.0\program\soffice.exe"',
						"The command to open libreoffice (in Linux, just 'libreoffice' should be enough"),
				)
FIConstants=FIConstantsAbstarct()
