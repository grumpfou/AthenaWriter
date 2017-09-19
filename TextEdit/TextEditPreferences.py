"""
Part of the  project AthenaWriter. Written by Renaud Dessalles
Contains the class that deal with the configuration of the core program.

"""
############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from PyQt5 import QtGui, QtCore, QtWidgets
from ConstantsManager.ConstantsManager import CMConstantsManager


class TEPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(

		RECHECK_TEXT_OPEN 	 = (bool,False),
		DO_TYPOGRAPHY		 = (bool,True),
		AUTO_CORRECTION      = (bool,True),
		LIM_RECURSIV_UNDO    = (int	,100),
		FIND_LEN_CONTEXT 	 = (int	,10),
		SPELL_CHECK 		 = (bool,True),
		TEXT_INDENT		 	 = (int,50),
		TEXT_LINE_HEIGHT	 = (int,100),
		TEXT_MARGIN		 	 = (float,50),
		ZOOM_INCREMENT	 	 = (int,3),
		ZOOM_DEFAULT	 	 = (int,20),
			)
	descriptions 	= dict(
		RECHECK_TEXT_OPEN 	 = "Will recheck the typography of the file "+\
			"when opening",
		DO_TYPOGRAPHY		 = "Will perform the typography checking while "+\
			"writing",
		AUTO_CORRECTION      = "Will perform the word auto-correction while "+\
			"writing",
		LIM_RECURSIV_UNDO    = "The limit of recursion to come back before "+\
			"the typography correction while making an undo",
		FIND_LEN_CONTEXT 	 = "Number of chars in which the context is "+\
			"inserted when searching for a pattern.",
		SPELL_CHECK 		 = "Set whenever the spelling needs to be check",
		TEXT_INDENT		     = "Indentation width of the text in the TextEdit",
		TEXT_LINE_HEIGHT	 = "Height of the interline in the TextEdit",
		TEXT_MARGIN		     = "Margin of the text edit",
		ZOOM_INCREMENT		 = "How much the zoom be increamented per action",
		ZOOM_DEFAULT		 = "The default font size of the normal text",

						)
TEPreferences=TEPreferencesAbstarct()


def yieldBlockInSelection_WW(self,direction=1):
	"""
	- direction : if positive, then will go forward otherwise, it will go
			backward.
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
		# if direction>=0:bl=bl.previous()
		else:bl=bl.previous()
		yield bl
QtGui.QTextCursor.yieldBlockInSelection=yieldBlockInSelection_WW


class TextEditFormatError (BaseException):
	def __init__(self,raison,position=False):
		"""
		Special Error in TextEdit error.
		"""
		self.raison	= raison
		self.position	= position
		print(self)
	def __str__(self):
		res=""
		if self.position:
			res+="In position "+str(self.position)+": "

		res+=self.raison

		return res.encode('ascii','replace')

TEHasEnchant = True

try :
	import enchant
except ImportError as e:
	print("Module Enchant not found !!!")
	TEHasEnchant = False
