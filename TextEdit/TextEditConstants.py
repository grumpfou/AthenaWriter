"""
Part of the  project. Written by Renaud Dessalles
Contains the class that deal with the configuration of the core program.

"""


from PyQt4 import QtGui, QtCore

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
	sys.path.append(dir) # to be able to import TextFormat
	dir 	= os.path.join(dir,'ConstantsManagement')

	foo = imp.find_module('ConstantsManagementConstantsAbstarct', [dir])
	foo = imp.load_module('ConstantsManagementConstantsAbstarct',*foo)
	CMConstantsAbstarct=foo.CMConstantsAbstarct
############################################################






class TEConstantsAbstract (CMConstantsAbstarct):
	all_constants=dict(	
				RECHECK_TEXT_OPEN 	 		= (bool		,False		, "Will recheck the typography of the file when opening"),
				DO_TYPOGRAPHY		 		= (bool		,True       , "Will perform the typography checking while writing"),
				AUTO_CORRECTION      		= (bool		,True       , "Will perform the word auto-correction while writing"),
				DFT_WRITING_LANGUAGE 		= (str		,"English"  , "The default writing language"),
				LIM_RECURSIV_UNDO    		= (int		,100        , 
									"The limit of recursion to come back before the typography correction while making an undo"),
				FIND_LEN_CONTEXT 		= (int		,10  , "Number of chars in which the context is inserted when searching for a pattern."),
				SPELL_CHECK 		= (bool ,True  , "Set whenever the spelling needs to be check"),
				
						)
TEConstants= TEConstantsAbstract()

	
def yieldBlockInSelection_WW(self,direction=1):
	"""
	-direction : if positive, then will go forward
		otherwise, it will go backward.
	"""
	pos1=self.selectionStart()
	pos2=self.selectionEnd ()
	
	startCursor=QtGui.QTextCursor(self)
	endCursor=QtGui.QTextCursor(self)
	startCursor.setPosition(pos1)
	endCursor  .setPosition(pos2)

	if direction>=0:
		bl=startCursor.block()
		bl_end=endCursor.block()
	else:
		bl=endCursor.block()
		bl_end=startCursor.block()

	yield bl
	while bl!=bl_end:
		if direction>=0:bl=bl.next()
		if direction>=0:bl=bl.previous()
		yield bl
QtGui.QTextCursor.yieldBlockInSelection=yieldBlockInSelection_WW

	
class TextEditFormatError (BaseException):
	def __init__(self,raison,position=False):
		"""
		Special Error in TextEdit error.
		"""
		self.raison	= raison
		self.position	= position
		print self
	def __str__(self):
		res=""
		if self.position:
			res+="In position "+str(self.position)+": "
		
		res+=self.raison
		
		return res.encode('ascii','replace')
