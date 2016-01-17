from PyQt4 import QtGui, QtCore

from AthenaWriterPreferences import *
from AthenaWriterCore import AWCore
# from ConfigLoading.ConfigLoadingLastFiles import CLLastFiles
from ConfigLoading.ConfigLoadingPreferencesDialog import CLPreferencesDialog
from ConstantsManager.ConstantsManagerWidget import CMDialog
from ConstantsManager.ConstantsManager import CMConstantsManager
from DocProperties.DocPropertiesStatistics import DPStatisticsDialog
from DocExport.DocExportDialog import DEDialog
from FileManagement.FileManagement import FMFileManagement
from FileManagement.FileManagementLastFiles import FMLastFilesFile
from TextEdit.TextEdit import TETextEdit
from TextLanguages.TextLanguages import TLDico
from TextStyles.TextStyles import TSManager


import sys
import os
import threading
import time
import codecs
import subprocess
		

		
class AWWriterText(QtGui.QMainWindow,AWCore):
	def __init__(self,*args,**kargs):
		
		QtGui.QMainWindow.__init__(self,*args,**kargs)
		AWCore.__init__(self)
		# dict_autocorrection = FMAutoCorrectionFile.open()
		
		
		self.textEdit = TETextEdit(
						language_name=TLPreferences['DFT_WRITING_LANGUAGE'])
		
		self.setCentralWidget (self.textEdit)
		
		self.fullScreened=False
		
		self.setup_actions()
		self.setup_connections()
		self.setup_menus()
		
		self.setWindowTitle("AthenaWriter : NewFile")
		self.setGeometry(100,100,AWPreferences["INIT_SIZE_X"],
												AWPreferences["INIT_SIZE_Y"])
		self.changeMessageStatusBar("Welcome in AthenaWriter :)")
		
		if AWPreferences['AUTOSAVE']:
			self.timer(start=True)
		
		# self.setGeometry(100,100,500,1000)
		
	def setup_actions(self):
		self.actionFileSave 	= QtGui.QAction("Save"			,self)
		self.actionFileSaveAs 	= QtGui.QAction("Save as"		,self)
		self.actionFileNew 		= QtGui.QAction("New"			,self)
		self.actionFileOpen		= QtGui.QAction("Open"			,self)
		self.actionFileImport	= QtGui.QAction("Import"		,self)
		self.actionFileExport	= QtGui.QAction("Export"		,self)
		self.actionFileStats	= QtGui.QAction("Statistics"	,self)
		self.actionFileMetaData	= QtGui.QAction("Meta-data"	    ,self)
		self.actionFileQuit		= QtGui.QAction("Quit"			,self)
		
		self.actionRecentFilesList = []
		# dico=self.language.shortcuts_insert
		for path in self.lastFiles.list_files: 
			#create the actions to open the last files
			act = QtGui.QAction(path,self)
			self.actionRecentFilesList.append(act)
		
		self.actionSendToExternalSoftware = QtGui.QAction(
										"Send to external software"	,self)
		self.actionEditPreferences = QtGui.QAction("Preferences"	,self)
		# self.actionViewZoomIn		= QtGui.QAction("Zoom in"		,self)
		# self.actionViewZoomOut		= QtGui.QAction("Zoom out"		,self)
		# self.actionViewZoomDft		= QtGui.QAction("Zoom default"	,self)
		self.actionViewFullScreen	= QtGui.QAction("FullScreen"	,self)
		
		self.actionAboutHelp	= QtGui.QAction("Help"			,self)
		self.actionAboutAbout	= QtGui.QAction("About WolfText",self)
		
		self.actionFileSave.setShortcuts(QtGui.QKeySequence.Save)
		self.actionFileSaveAs.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+S")) #TODO for Windows
		self.actionFileNew.setShortcuts(QtGui.QKeySequence.New)
		self.actionFileOpen.setShortcuts(QtGui.QKeySequence.Open)
		# self.actionFileStats.setShortcuts(QtGui.QKeySequence.Stats)
		self.actionFileQuit.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+Q")) #TODO for Windows
		self.actionFileSave.setEnabled(False)
		
		self.actionViewFullScreen.setShortcuts(QtGui.QKeySequence("F11"))
		
		# TODO: fix Import
		self.actionFileImport.setEnabled(False)
		
		
	def setup_connections(self):
		trig = QtCore.SIGNAL("triggered()")
		self.connect(self.actionFileSave	,trig,self.SLOT_actionFileSave	)
		self.connect(self.actionFileSaveAs	,trig,self.SLOT_actionFileSaveAs)
		self.connect(self.actionFileNew		,trig,self.SLOT_actionFileNew	)
		self.connect(self.actionFileOpen	,trig,self.SLOT_actionFileOpen	)
		self.connect(self.actionFileImport	,trig,self.SLOT_actionFileImport)
		self.connect(self.actionFileExport	,trig,self.SLOT_actionFileExport)
		self.connect(self.actionFileStats	,trig,self.SLOT_actionFileStats	)
		self.connect(self.actionFileMetaData,trig,self.SLOT_actionFileMetaData)
		self.connect(self.actionFileQuit	,trig,self.close				)
		
		self.connect(self.actionSendToExternalSoftware, trig,
				self.SLOT_actionSendToExternalSoftware)
		self.connect(self.actionEditPreferences, trig,
				self.SLOT_actionEditPreferences)
		
		# Add last file list
		mapper = QtCore.QSignalMapper(self)
		for path,act in zip(self.lastFiles.list_files,self.actionRecentFilesList):
			QtCore.QObject.connect(act,QtCore.SIGNAL("triggered ()"), mapper, QtCore.SLOT("map()"))
			# short.setContext(QtCore.Qt.WidgetShortcut)
			mapper.setMapping(act, path)
		self.connect(mapper, QtCore.SIGNAL("mapped(const QString &)"), self.SLOT_actionFileOpen )
		
		self.connect(self.actionViewFullScreen	,QtCore.SIGNAL("triggered()"),
				self.SLOT_actionViewFullScreen)
		
		self.connect(self.actionAboutHelp,QtCore.SIGNAL("triggered()"),
				self.SLOT_actionAboutHelp)
		self.connect(self.actionAboutAbout,QtCore.SIGNAL("triggered()"),
				self.SLOT_actionAboutAbout)
		
		self.connect(
				self.textEdit,
				QtCore.SIGNAL('textChanged ()'), 
				self.SLOT_somethingChanged
				)
		self.connect(
				self.textEdit,
				QtCore.SIGNAL('somethingChanged ()'), 
				self.SLOT_somethingChanged
				)
				
		self.connect(
				self.textEdit,
				QtCore.SIGNAL('typographyModification (PyQt_PyObject)'), 
				self.SLOT_typographyModification
				)
				
		self.connect(
				self.textEdit,
				QtCore.SIGNAL('protectedStyleModification (PyQt_PyObject)'), 
				self.SLOT_protectedStyleModification
				)
		
		
		
	def setup_menus(self):
		menuFile = self.menuBar().addMenu ( "File" )		
		menuFile.addAction(self.actionFileNew)
		menuFile.addAction(self.actionFileOpen)	
		menuRecentFiles = menuFile.addMenu ("RecentFiles")
		for act in self.actionRecentFilesList:
			menuRecentFiles.addAction(act)
		menuFile.addSeparator ()
		menuFile.addAction(self.actionFileSave)
		menuFile.addAction(self.actionFileSaveAs)		
		menuFile.addSeparator ()
		menuFile.addAction(self.actionFileImport)	
		menuFile.addAction(self.actionFileExport)
		menuFile.addSeparator ()
		menuFile.addAction(self.actionFileQuit)		
		
		menuEdit = self.menuBar().addMenu ( "Edit" )
		menuEdit.addAction(self.textEdit.actionUndo)
		menuEdit.addAction(self.textEdit.actionRedo)
		menuEdit.addSeparator ()		
		menuEdit.addAction(self.textEdit.actionCopy)
		menuEdit.addAction(self.textEdit.actionCut)
		menuEdit.addAction(self.textEdit.actionPaste)
		menuEdit.addSeparator ()		
		menuEdit.addAction(self.textEdit.actionLaunchFindDialog)		
		menuEdit.addAction(self.textEdit.actionFindNext)		
		menuEdit.addAction(self.textEdit.actionFindPrevious)		
		menuEdit.addAction(self.textEdit.actionLaunchCharWidgetTable)		
		menuEdit.addSeparator ()		
		# menuEdit.addAction(self.textEdit.actionChangeLanguage)
		menuEdit.addAction(self.actionEditPreferences)
		
		menuDocument = self.menuBar().addMenu ( "Document" )
		menuDocument.addAction(self.textEdit.actionRecheckTypography)
		menuDocument.addAction(self.textEdit.actionEnableTypo)
		menuDocument.addSeparator ()
		menuDocument.addAction(self.actionFileStats)
		menuDocument.addAction(self.actionFileMetaData)
		menuDocument.addSeparator ()		
		menuDocument.addAction(self.actionSendToExternalSoftware)
		
		menuStyle = self.menuBar().addMenu ( "Styles" )
		for id in TSManager.dictCharStyle.keys():
			if id in self.textEdit.actionStylesDict.keys():
				menuStyle.addAction(self.textEdit.actionStylesDict[id])
		menuStyle.addSeparator ()
		for id in TSManager.dictBlockStyle.keys():
			if id in self.textEdit.actionStylesDict.keys():
				menuStyle.addAction(self.textEdit.actionStylesDict[id])
		menuStyle.addSeparator ()
		menuStyle.addAction(self.textEdit.actionInsertImage)
		menuStyle.addSeparator ()
		menuStyle.addAction (self.textEdit.actionResetStyle)
		
		
		menuView = self.menuBar().addMenu ( "View" )
		menuView.addAction(self.actionViewFullScreen)
		

		
		menuAbout		= self.menuBar().addMenu ( "About" )
		menuAbout.addAction(self.actionAboutHelp)
		menuAbout.addAction(self.actionAboutAbout)
		
		list_actions = [ self.actionFileNew,self.actionFileOpen,
			self.actionFileImport,self.actionFileSave,self.actionFileSaveAs,
			self.actionFileExport,self.actionFileStats,self.actionFileMetaData,
			self.actionFileQuit,self.actionViewFullScreen,
			self.textEdit.actionUndo,self.textEdit.actionRedo,
			self.textEdit.actionCopy,self.textEdit.actionCut,
			self.textEdit.actionPaste, self.textEdit.actionLaunchFindDialog,
			self.textEdit.actionFindNext,self.textEdit.actionFindPrevious,
			self.textEdit.actionLaunchCharWidgetTable,
			# self.textEdit.actionChangeLanguage,
			self.textEdit.actionRecheckTypography,
			self.textEdit.actionEnableTypo,self.actionSendToExternalSoftware,
			self.actionAboutHelp,self.actionAboutAbout] + \
			self.textEdit.actionStylesDict.values()
		for act in list_actions:
			self.addAction(act)
			
	################################## SLOTS ##################################
	def SLOT_actionFileSave(self):
		"""
		Slot used when saving the current file.
		"""		
		if self.filepath==None:
			filepath = FMFileManagement.save_gui_filepath(
					self.get_default_opening_saving_site(),
					self,filter="AthW files (*.athw);; All files (*.*)")
		else:
			filepath = self.filepath
		if filepath :
			filepath=unicode(filepath)
			
			
			progressBar = QtGui.QProgressBar(parent=self)
			progressBar.setMaximum(0)
			progressBar.setValue(0)
			# center the widget
			point = self.geometry().center()
			point1 = progressBar.geometry().center()
			progressBar.move(point-point1)
			# set the window to the correct flag
			progressBar.setWindowFlags(QtCore.Qt.SplashScreen)
			progressBar.setWindowModality(QtCore.Qt.WindowModal)
			
			progressBar.show()
			
			# this class is a very classic thread just to save the file while
			# displaying the progressBar:
			class TaskThread(QtCore.QThread):
				taskFinished = QtCore.pyqtSignal()
				def run(self1):
					self.CMD_FileSave(filepath=filepath)
					self1.taskFinished.emit()
					
			# What we have to do at the end of the saving
			def finishing():
				progressBar.close()
				self.actionFileSave.setEnabled(False)
				self.setWindowTitle("AthenaWriter : "+self.filepath)
				tmp,filename = os.path.split(self.filepath)
				self.changeMessageStatusBar("Has saved "+filename)
				self.lastFiles.addFile(self.filepath)
			
			self.myLongTask = TaskThread()
			self.connect(self.myLongTask,QtCore.SIGNAL("taskFinished()"),
																	finishing)
					
			# self.myLongTask.taskFinished.connect(finishing)
			self.myLongTask.start()
			
			
			

	def SLOT_actionFileSaveAs(self):
		"""
		Slot used when saving as the current file.
		"""
		filepath = FMFileManagement.save_gui_filepath(
				self.get_default_opening_saving_site(),
				self,filter="AthW files (*.athw);; All files (*.*)")
		if filepath :
			self.clean_tmp_files() # we remove the previous tmp files
			self.CMD_FileSave(filepath=unicode(filepath))
			self.actionFileSave.setEnabled(False)
			self.setWindowTitle("AthenaWriter : "+self.filepath)
			tmp,filename = os.path.split(self.filepath)
			self.changeMessageStatusBar("Has saved "+filename)
			self.lastFiles.addFile(self.filepath)
			
	def SLOT_actionFileNew(self):
		"""
		Slot used when creating a new file.
		"""
		res=self.doSaveDialog()
		if (res != QtGui.QMessageBox.Yes) and (res != QtGui.QMessageBox.No):
			return False
		self.clean_tmp_files() # we remove the previous tmp files
		self.textEdit.setText("")
		self.filepath=None
		self.metadata=DPMetaData()
		self.setWindowTitle("AthenaWriter : NewFile")
		self.changeMessageStatusBar("Created a new file")

		return True
		
	def SLOT_actionFileOpen(self,filepath=None):
		"""
		If filepath==None, it will display the window to search the file
		If filepath==None, it will display the window to search the file
		"""
		res=self.doSaveDialog()
		if (res != QtGui.QMessageBox.Yes) and (res != QtGui.QMessageBox.No):
			return False
		if filepath==None:
			filepath = FMFileManagement.open_gui_filepath(
					self.get_default_opening_saving_site(),
					self,filter="AthW files (*.athw);; All files (*.*)")			
		else :
			filepath=str(filepath)
		if filepath:
			self.clean_tmp_files() # we remove the previous tmp files
			try:
				self.CMD_FileOpen(filepath)
			except IOError:
				# if the file do not exist, propose to crreate it
				r = QtGui.QMessageBox.question(self,"Non existing file",
					"The file "+filepath+" do not exist. Do you want to "+\
					"create it ?",
					QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
					
				if r!= QtGui.QMessageBox.Yes:
					return False
				self.filepath = filepath
				
			self.actionFileSave.setEnabled(False)

			self.setWindowTitle("AthenaWriter : "+self.filepath)
			tmp,filename = os.path.split(filepath)
			self.changeMessageStatusBar("Has opened "+filename)
			self.lastFiles.addFile(self.filepath)
			
			return True
		else:
			return False
			
	def SLOT_actionFileImport(self,filepath=None):
		"""
		If filepath==None, it will display the window to search the file
		"""
		res=self.doSaveDialog()
		if (res != QtGui.QMessageBox.Yes) and (res != QtGui.QMessageBox.No):
			return False
		if filepath==None:
			filepath = FMFileManagement.open_gui_filepath(
					self.get_default_opening_saving_site(),
					self)			
		else :
			filepath=str(filepath)
		if filepath:
			self.clean_tmp_files() # we remove the previous tmp files
			path,e = os.path.splitext(filepath)
			e = e[1:]#the [1:] is to skip the dot in the extension
			self.CMD_FileImport(filepath=filepath,format_name=e)
			
			self.actionFileSave.setEnabled(True)			
			self.setWindowTitle("AthenaWriter : NewFile")
			tmp,filename = os.path.split(filepath)
			self.changeMessageStatusBar("Has imported "+filename)
			return True
		else:
			return False
			
	def SLOT_actionFileExport(self):
		dft_opening_saving_site = self.get_default_opening_saving_site()
		if self.filepath!=None:
			res = DEDialog.getFields(
					dft_opening_saving_site=dft_opening_saving_site,
					default_path = self.filepath,
					)
		else:
			res = DEDialog.getFields(
					dft_opening_saving_site=dft_opening_saving_site,
					)
			
		if res :
			try :
				res1 = self.CMD_FileExport(**res)
			except IOError,e:
				print e
				res1 = False
			if res1:
				msg = "Successfull exportation"
				self.changeMessageStatusBar("Has exported "+res['filepath'])
				dia = QtGui.QMessageBox.information ( 
						self, 
						"Exportation" , 
						msg)
			else:
				msg = "Unsuccessfull exportation :\n"
				msg += str(e)
				dia = QtGui.QMessageBox.critical ( 
						self, 
						"Exportation" , 
						msg)
				
		# import TextFormat.TextFormat
		# list_extension = [format.extension for format in FEList]
		# res = QtGui.QInputDialog. getItem (self,'Export',
								# 'Format of the exportation:', list_extension)
		# if res[1]:
			# res1 = self.CMD_FileExport(format_name = str(res[0]))
			# if res1:
				# self.changeMessageStatusBar("Has exported "+res1)
				# return True
		# return False
				
			
	def SLOT_actionFileStats(self):
		dialog = DPStatisticsDialog(textedit=self.textEdit,parent=self)
		dialog.show()
	def SLOT_actionFileMetaData(self):
		
			
		# constraints_dict = {'language': [TLDico.keys()] }
		d = CMDialog.getValueDict(parent=self,
				constants_manager = self.metadata,
				skip_same_as_init = True
				)
		if d and len(d)>0 :
			self.metadata.update(d)
			if 'language' in d.keys() and not self.textEdit.document().isEmpty():
				self.textEdit.changeLanguage(language_name = unicode(d['language']))
				r = QtGui.QMessageBox.question(self, "Recheck Typography", 
					"Do you want to import the recheck the typography ?",
					QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
				if r== QtGui.QMessageBox.Yes:
					self.textEdit.SLOT_actionRecheckTypography()
			self.SLOT_somethingChanged()
					
		# dialog = MDMetaDataDialog(metadata=self.metadata,parent=self)
		# dialog.show()
	def SLOT_actionViewFullScreen(self):
		if not self.fullScreened:
			self.showFullScreen()
			self.textEdit.setVerticalScrollBarPolicy(
					QtCore.Qt.ScrollBarAlwaysOff)
			self.menuBar().setHidden(True)
			if AWPreferences['FULLSCREEN_CENTRAL_MAX_SIZE']>0:
				rec = QtGui.QApplication.desktop().screenGeometry()
				marg = rec.width()
				marg -= AWPreferences['FULLSCREEN_CENTRAL_MAX_SIZE']
				marg *= .5
				if marg >0:
					self.setContentsMargins ( marg, 0, marg, 0)
				else :
					print "CAUTION : FULLSCREEN_CENTRAL_MAX_SIZE too high"
				
			self.fullScreened=True
		else : 
			self.showNormal()
			self.setContentsMargins ( 0,0,0, 0)
			self.textEdit.setVerticalScrollBarPolicy(
					QtCore.Qt.ScrollBarAsNeeded)
			self.fullScreened=False
	def SLOT_actionAboutHelp(self):
		pass
	def SLOT_actionAboutAbout(self):
		pass
	def SLOT_somethingChanged(self):
		self.actionFileSave.setEnabled(True)
		if self.filepath==None:
			self.setWindowTitle("AthenaWriter : *NewFile")
		else :
			self.setWindowTitle("AthenaWriter : *"+self.filepath)
	
	def SLOT_typographyModification(self,modification):
		self.changeMessageStatusBar(modification[0].title)
	def SLOT_protectedStyleModification(self,mess):
		self.changeMessageStatusBar(mess)
		
	def SLOT_autosave(self):
		if self.filepath!=None:
			direct,file=os.path.split(self.filepath)
			tmp_filepath = os.path.join(direct,
					AWPreferences['TMP_FILE_MARK']+file)
			res = FMFileManagement.save(
					unicode(self.textEdit.toXml()),tmp_filepath)
			
	def SLOT_actionSendToExternalSoftware (self):
		# Send the scene to another software (mine is called Antidote and 
		# accept only a certain type of encoding).
		path=AWPreferences['EXTERNAL_SOFT_PATH']
		if path=="":
			QtGui.QMessageBox.information(self,
			"External Software Sender",
			"Sorry, there is no path to the external software in the "+\
			"configuration file.")
			return False
			
		text=self.textEdit.toXml()
		i=0
		while AWPreferences['TMP_FILE_MARK']+"tmp"+str(i).zfill(3)+'.txt' in \
															os.listdir('.'):
			i+=1
		name=AWPreferences['TMP_FILE_MARK']+"tmp"+str(i).zfill(3)+'.txt'
		FMFileManagement.save(text,name, encoding='utf-8-sig', mode='w')
		s=subprocess.Popen(path+' '+os.path.abspath(name))
		
		res = QtGui.QMessageBox.question(self, "External Software Sender", 
				"Have you finished to correct the file?", 
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
		

		if (res == QtGui.QMessageBox.Yes) :
			text = FMFileManagement.open(name, encoding='utf-8-sig', mode='rb')
			self.textEdit.setText(text,type='xml')
	
	def SLOT_actionEditPreferences(self):
		d = CLPreferencesDialog.getValueDict(
			dict_preferences = AWDictPreferences,parent=self)
		if d:
			AWOverwritePreferences(d)
			pref_dict , descr_dict = AWPreferencesToDict(skip_same_as_dft=True)
			CLPreferencesFiles.replace(dict_to_save=pref_dict,
													descriptions=descr_dict)
		
		
	def closeEvent(self, event):
		"""Check if we have changed something without saving"""
		res=self.doSaveDialog()
		if (res == QtGui.QMessageBox.Yes) or (res == QtGui.QMessageBox.No):
			FMLastFilesFile.save(self.lastFiles.list_files)
			self.clean_tmp_files()
			if AWPreferences['AUTOSAVE']: #We stop the thread of the autosave
				self.threading_autosave.cancel()
			event.accept()
		else:
			event.ignore()
		
	###########################################################################
		
	def get_default_opening_saving_site(self):
		"""When open a file dialog, in which directory the dialog window 
		should begin :
		"""
		if self.filepath== None:
			return os.path.expanduser(AWPreferences['DLT_OPEN_SAVE_SITE'])
		else :
			res,tmp=os.path.split(self.filepath)
			return res		
	
	def doSaveDialog(self):
		"""
		Check if there is any modifications and ask if it has to save the file 
		if it not the case.		
		"""
		if self.actionFileSave.isEnabled(): 
			res=QtGui.QMessageBox.question(
					self,
					"Modification", "Do you want to save the modifications",
					QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | \
					QtGui.QMessageBox.Cancel
					)
			if (res == QtGui.QMessageBox.Yes):
				self.SLOT_actionFileSave()
			return res
		return QtGui.QMessageBox.Yes 
		
	def changeMessageStatusBar(self,message=None):
		"""This function is called to display a message in the status bar"""
		if message==None: message=u""
		self.statusBar().showMessage(message,
											AWPreferences['TIME_STATUS_MESSAGE'])

	def timer(self,start=False):
		self.threading_autosave = threading.Timer(
				AWPreferences['AUTOSAVE_TEMPO'], self.timer)
		self.threading_autosave.start()
		if not start:
			self.changeMessageStatusBar('Autosave')
			self.SLOT_autosave()

	def clean_tmp_files(self):
		if self.filepath!=None:
			direct,file=os.path.split(self.filepath)
			tmp_filepath = os.path.join(direct,
					AWPreferences['TMP_FILE_MARK']+file)
			try:
				os.remove(tmp_filepath)
			except : pass

if __name__ == '__main__':
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
				
