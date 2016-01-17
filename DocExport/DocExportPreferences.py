############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from ConstantsManager.ConstantsManager import CMConstantsManager
import subprocess

class DEPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(	
		PDFLATEX_COMMAND	= (str	,r'pdflatex'),
		EBOOKCONVERT_COMMAND	= (str	,r'ebook-convert'),
		PANDOC_COMMAND = (str,"pandoc"),
			)
			
	descriptions 	= dict(	
		PDFLATEX_COMMAND	 = "The command to open pdflatex (in Linux, "+\
				"just 'pdflatex' should be enough)",
		EBOOKCONVERT_COMMAND = "The command to open ebook-convert calibre "+\
				"conversion (in Linux, just 'ebook-convert' should be enough)",
		PANDOC_COMMAND = "The command to open pandoc (in Linux, just "+\
				"'pandoc' should be enough).",
		)
DEPreferences = DEPreferencesAbstarct()



def DETestPdfLatext():
	try : 
		return subprocess.check_call(
				[DEPreferences['PDFLATEX_COMMAND'],'--version'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)==0
	except OSError:
		return False

def DETestEbookConvert():
	try : 
		return subprocess.check_call(
				[DEPreferences['EBOOKCONVERT_COMMAND'],'--version'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)==0
	except OSError:
		return False
		
def DETestPandoc():
	try : 
		return subprocess.check_call(
				[DEPreferences['PANDOC_COMMAND'],'--version'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)==0
	except OSError:
		return False



	
