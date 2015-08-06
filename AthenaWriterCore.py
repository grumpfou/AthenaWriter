from PyQt4 import QtGui, QtCore

from AthenaWriterConstants import *
from TextEdit.TextEdit import TETextEdit
from TextEdit.TextEditLanguages import TELanguageDico
from TextStyles.TextStyles import TSManager
from DocStatistics.DocStatistics import DSDialogManager
from FileManagement.FileManagement import FMFileManagement
from FileManagement.FileManagementAutoCorrection import FMAutoCorrectionFile
from FileManagement.FileManagementLastFiles import FMLastFilesFile
from FileExport.FileExportExport import FEList
from FileImport.FileImport import FIList
from LastFiles.LastFiles import LFList
from MetaData.MetaData import MDMetaDataDialog,MDMetaData
from ConstantsManagement.ConstantsManagementDialog import CMDialog



import sys
import os
import threading
import time
import codecs
import subprocess

class AWCore:
	class Error (Exception):
		def __init__(self,raison):
			self.raison = raison

		def __str__(self):
			return self.raison.encode('ascii','replace')

	def __init__(self):
		self.textEdit = TETextEdit(language_name='French')
		self.metadata = MDMetaData()
		self.filepath=None
		self.lastFilesList=LFList(FMLastFilesFile.open())

		
	def CMD_FileSave(self,filepath=None):
		if filepath==None:
			if self.filepath==None:
				raise self.Error('Please specify the filepath')
			filepath = self.filepath
		else:
			self.filepath = filepath
		res = FMFileManagement.save(unicode(self.textEdit.toXml()),filepath)
		
		if res :
			if AWConstants['DO_METADATA'] and not self.metadata.isEmpty(): 
				# we will save the file .athw_meta as well
				cur = self.textEdit.textCursor()
				self.metadata.lastpos = int(cur.position())
				self.metadata.language = self.textEdit.language.name
				
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
		print 'filepath : ',filepath
		text = FMFileManagement.open(filepath)
		
		if AWConstants['DO_METADATA'] :
			meta_filepath,tmp = os.path.splitext(self.filepath)
			meta_filepath += '.athw_meta'
			if os.path.exists(meta_filepath):
				self.metadata=MDMetaData.init_from_xml_string(
									FMFileManagement.open(meta_filepath))
			else:
				self.metadata=MDMetaData()
			print 'self.metadata.__dict__ : ',self.metadata.__dict__
			language = self.metadata.language
			lastpos = self.metadata.lastpos
			
			self.textEdit.setText(text,type='xml',local_dir=local_dir,new_language=language)
			if lastpos != None:
				cur = self.textEdit.textCursor()
				cur.setPosition(lastpos)
				self.textEdit.setTextCursor(cur)
		else:
			self.textEdit.setText(text,type='xml',local_dir=local_dir)
			
		return True
	
	def CMD_FileImport(self,filepath,format_name,to_skip=None):
		"""
		- filepath : the path to the file to import
		- format_name : the name of the format
		- to_skip : the list of the lines to skip
		"""
		if to_skip==None : to_skip=[]
		# We check whenever we can import this type of files
		list_extentions = [format.extension for format in FIList]
		if format_name not in list_extentions:
			raise self.Error('Unknown format to import: choose in '+\
														str(list_extentions))
		
		
		fiimport_instance = FIList[list_extentions.index(format_name)](
														file=filepath)
		fiimport_instance.import2xml()
		for i in to_skip:
			fiimport_instance.skipLine(i)
		text = fiimport_instance.text
		self.textEdit.setText(text,type='xml')
		self.filepath = None
		

	def CMD_FileExport(self,format_name,filepath=None,check_typo=False,\
																	**kargs):
		if check_typo:
			self.textEdit.SLOT_actionRecheckTypography()
		list_extentions = [format.extension for format in FEList]
		if format_name not in list_extentions:
			raise self.Error('Unknown format to import: choose in '+\
														str(list_extentions))
		index = list_extentions.index(format_name)
		format = FEList[index](TSManager)
		# if len(kargs)==0 and AWConstants['DO_METADATA']:
			# kargs=self.metadata.getDict()
		
	
		format.export(self.textEdit,**kargs)
		res = format.export_file(
#				default_saving_site=self.get_default_opening_saving_site(),
				parent=self,
				filepath=filepath,
				)
				
		return res

if __name__ == '__main__':
	from AthenaWriterMainWindow import AWWriterText

	app = QtGui.QApplication(sys.argv)
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
				
