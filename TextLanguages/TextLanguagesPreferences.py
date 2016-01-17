############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from PyQt4 import QtGui, QtCore
from ConstantsManager.ConstantsManager import CMConstantsManager


class TLPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(
			DFT_WRITING_LANGUAGE = (str	,"English"),
			)
			
	descriptions 	= dict(
			DFT_WRITING_LANGUAGE = "The default writing language",
			)
TLPreferences=TLPreferencesAbstarct()
