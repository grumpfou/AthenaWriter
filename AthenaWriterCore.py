__version__ = "1.1beta"

AWAbout = """
Athena Writer (version %s) is a software written by Renaud Dessalles (Grumpfou).
It is deseigned as a companion for the writting of short stories. It is
distrationless and helps to respect the typography.

It is published under the license under the license GNU General Public License
v3.0.

See https://github.com/grumpfou/AthenaWriter .
"""%__version__

from PyQt5 import QtGui, QtCore, QtWidgets

from AthenaWriterPreferences import *
from TextEdit.TextEdit import TETextEdit
from TextStyles.TextStyles import TSManager
from FileManagement.FileManagement import FMFileManagement
from FileManagement.FileManagementAutoCorrection import FMAutoCorrectionFile
from FileManagement.FileManagementLastFiles import FMLastFilesFile
from DocExport.DocExport import DEList
from DocImport.DocImport import DIDict
from ConfigLoading.ConfigLoadingLastFiles import CLLastFiles
from DocProperties.DocPropertiesMetaData import DPMetaData

import sys
import os
import threading
import time
import codecs
import subprocess
import itertools

class AWCore:
	class Error (Exception):
		def __init__(self,raison):
			self.reason = raison

		def __str__(self):
			return self.reason

	def __init__(self):
		self.textEdit = TETextEdit(language_name=
										TLPreferences['DFT_WRITING_LANGUAGE'])
		self.metadata = DPMetaData()
		self.filepath=None
		self.lastFiles=CLLastFiles(FMLastFilesFile.open())


	def CMD_FileSave(self,filepath=None):
		if filepath==None:
			if self.filepath==None:
				raise self.Error('Please specify the filepath')
			filepath = self.filepath
		else:
			self.filepath = filepath
		res = FMFileManagement.save(str(self.textEdit.toXml()),filepath)

		if res :
			if not self.metadata.isEmpty():
				# we will save the file .athw_meta as well
				cur = self.textEdit.textCursor()
				self.metadata.__setitem__('lastpos', int(cur.position()),
															protected=False)
				self.metadata['language'] = self.textEdit.language.name
				self.metadata.__setitem__('profile',
							self.textEdit.language.profile, protected=False)

				to_save = self.metadata.toxml()
				meta_filepath,tmp = os.path.splitext(self.filepath)
				meta_filepath += '.athw_meta'

				res = FMFileManagement.save(to_save,meta_filepath)

	def	CMD_FileSaveCopy(self,filepath):
		old_filepath = self.filepath
		self.CMD_FileSave(filepath)
		self.filepath = old_filepath

	def CMD_FileOpen(self,filepath):
		if filepath==None:
			if self.filepath==None:
				raise self.Error('Please specify the filepath')
			filepath = self.filepath
		else:
			self.filepath=filepath


		# Get the text:
		local_dir,tmp = os.path.split(self.filepath)
		text = FMFileManagement.open(filepath)

		meta_filepath,tmp = os.path.splitext(self.filepath)
		meta_filepath += '.athw_meta'
		if os.path.exists(meta_filepath):
			self.metadata=DPMetaData.init_from_xml_string(
								FMFileManagement.open(meta_filepath))
		else:
			self.metadata=DPMetaData()
		language = self.metadata['language']
		lastpos = self.metadata['lastpos']
		profile = self.metadata['profile']
		if profile == None:
			profile = TLPreferences['DFT_TYPO_PROFILE']
		self.textEdit.setText(text,type='xml',new_language=language,
															profile=profile)
		if lastpos != None:
			if lastpos==-1:
				lastpos = self.textEdit.document().characterCount()
			cur = self.textEdit.textCursor()
			cur.setPosition(lastpos)
			self.textEdit.setTextCursor(cur)

		return True

	def CMD_FileImport(self,filepath,format_name,to_skip=None):
		"""
		- filepath : the path to the file to import
		- format_name : the name of the format
		- to_skip : the list of the lines to skip
		"""
		if to_skip==None : to_skip=[]
		# We check whenever we can import this type of files
		list_extentions = list(DIDict.keys())

		if format_name not in list_extentions:
			raise self.Error(
				'Unknown format <%s> to import: choose in '%format_name+\
														str(list_extentions))


		fiimport_instance = DIDict[format_name]( file=filepath)
		fiimport_instance.import2xml()
		for i in to_skip:
			fiimport_instance.skipLine(i)
		text = fiimport_instance.text
		self.textEdit.setText(text,type='xml')

		self.textEdit.SLOT_actionRecheckTypography()
		self.filepath = None


	def CMD_FileExport(self,format_name,filepath=None,check_typo=False,\
																	**kargs):
		if check_typo:
			self.textEdit.SLOT_actionRecheckTypography()
		list_extentions = [format.name for format in DEList]
		if format_name not in list_extentions:
			raise self.Error('Unknown format to import: choose in '+\
														str(list_extentions))
		index = list_extentions.index(format_name)
		format = DEList[index](TSManager)

		format.export(self.textEdit,**kargs)
		res = format.export_file(
#				default_saving_site=self.get_default_opening_saving_site(),
				parent=self,
				filepath=filepath,
				)

		return res

if __name__ == '__main__':
	from AthenaWriterMainWindow import AWWriterText

	app = QtWidgets.QApplication(sys.argv)
	dir,f = os.path.split(__file__)
	iconpath = os.path.join(dir,'./Images/LogoTmp.png')
	app.setWindowIcon(QtGui.QIcon(iconpath))

	writerText = AWWriterText(parent=None)
	writerText.show()
	if len(sys.argv)>1:
		filepath=sys.argv[1]
		writerText.SLOT_actionFileOpen(filepath=filepath)

	import sys
	sys.exit(app.exec_())
