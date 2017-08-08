############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from PyQt5 import QtGui, QtCore, QtWidgets
from ConstantsManager.ConstantsManager import CMConstantsManager


class TLPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(
			DFT_WRITING_LANGUAGE = (str	,"English"),
			DFT_TYPO_PROFILE = (int,0),
			GUESS_NB_CHAR = (int,2000),
			)
			
	descriptions 	= dict(
			DFT_WRITING_LANGUAGE = "The default writing language",
			DFT_TYPO_PROFILE = "The default typography profile (0 is, "+\
				"strict 1 is medium, >=2 is loose)",
			GUESS_NB_CHAR = ("The number of char to consider to guess the "
				"language"),
			)
TLPreferences=TLPreferencesAbstarct()
