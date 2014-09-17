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

class FEConstantsAbstarct (CMConstantsAbstarct):
	all_constants=  dict(	
		PDFLATEX_COMMAND	= (str	,r'pdflatex',
				"The command to open pdflatex (in Linux, just 'pdflatex' "+\
				"should be enough"),
		EBOOKCONVERT_COMMAND	= (str	,r'ebook-convert',
				"The command to open ebook-convert calibre conversion (in "+\
				"Linux, just 'ebook-convert' should be enough"),
		)
FEConstants=FEConstantsAbstarct()
