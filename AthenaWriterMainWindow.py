from PyQt5 import QtGui, QtCore, QtWidgets

from AthenaWriterPreferences import *
from AthenaWriterCore import AWCore,AWAbout
from ConfigLoading.ConfigLoadingPreferencesDialog import CLPreferencesDialog
from ConstantsManager.ConstantsManagerWidget import CMDialog
from ConstantsManager.ConstantsManager import CMConstantsManager
from DocProperties.DocPropertiesStatistics import DPStatisticsDialog
from DocProperties.DocPropertiesMetaData import DPMetaData
from DocExport.DocExportDialog import DEDialog
from DocImport.DocImport import DIDict
from FileManagement.FileManagement import FMTextFileManagement
from TextEdit.TextEdit import TETextEdit
from TextStyles.TextStyles import TSManager


import sys
import os
import threading
import time
import codecs
import subprocess



class AWWriterText(QtWidgets.QMainWindow,AWCore):
	def __init__(self,*args,**kargs):

		QtWidgets.QMainWindow.__init__(self,*args,**kargs)
		AWCore.__init__(self)
		# dict_autocorrection = FMAutoCorrectionFile.open()


		self.textEdit = TETextEdit(parent=self,
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
		self.actionFileSave 	= QtWidgets.QAction("Save"			,self)
		self.actionFileSaveAs 	= QtWidgets.QAction("Save as"		,self)
		self.actionFileNew 		= QtWidgets.QAction("New"			,self)
		self.actionFileOpen		= QtWidgets.QAction("Open"			,self)
		self.actionFileImport	= QtWidgets.QAction("Import"		,self)
		self.actionFileExport	= QtWidgets.QAction("Export"		,self)
		self.actionFileStats	= QtWidgets.QAction("Statistics"	,self)
		self.actionFileMetaData	= QtWidgets.QAction("Meta-data"	    ,self)
		self.actionFileQuit		= QtWidgets.QAction("Quit"			,self)

		# self.actionFileExport.setEnabled(False) ######## TODO to debug

		self.actionRecentFilesList = []
		# dico=self.language.shortcuts_insert
		for path in self.lastFiles.getValues():
			#create the actions to open the last files
			act = QtWidgets.QAction(path,self)
			self.actionRecentFilesList.append(act)

		self.actionSendToExternalSoftware = QtWidgets.QAction(
										"Send to external software"	,self)
		self.actionEditPreferences = QtWidgets.QAction("Preferences"	,self)
		# self.actionViewZoomIn		= QtWidgets.QAction("Zoom in"		,self)
		# self.actionViewZoomOut		= QtWidgets.QAction("Zoom out"		,self)
		# self.actionViewZoomDft		= QtWidgets.QAction("Zoom default"	,self)
		self.actionViewFullScreen	= QtWidgets.QAction("FullScreen"	,self)

		self.actionAboutHelp	= QtWidgets.QAction("Help"			,self)
		self.actionAboutAbout	= QtWidgets.QAction("About Athena Writer",self)

		self.actionFileSave.setShortcuts(QtGui.QKeySequence.Save)
		self.actionFileSaveAs.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+S")) #TODO for Windows
		self.actionFileNew.setShortcuts(QtGui.QKeySequence.New)
		self.actionFileOpen.setShortcuts(QtGui.QKeySequence.Open)
		# self.actionFileStats.setShortcuts(QtGui.QKeySequence.Stats)
		self.actionFileQuit.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+Q")) #TODO for Windows
		self.actionFileSave.setEnabled(False)

		self.actionViewFullScreen.setShortcuts(QtGui.QKeySequence("F11"))

		# TODO: fix Import
		self.actionFileImport.setEnabled(True)


	def setup_connections(self):

		self.actionFileSave		.triggered.connect(self.SLOT_actionFileSave)
		self.actionFileSaveAs	.triggered.connect(self.SLOT_actionFileSaveAs)
		self.actionFileNew		.triggered.connect(self.SLOT_actionFileNew)
		self.actionFileOpen		.triggered.connect(self.SLOT_actionFileOpen)
		self.actionFileImport	.triggered.connect(self.SLOT_actionFileImport)
		self.actionFileExport	.triggered.connect(self.SLOT_actionFileExport)
		self.actionFileStats	.triggered.connect(self.SLOT_actionFileStats)
		self.actionFileMetaData	.triggered.connect(self.SLOT_actionFileMetaData)
		self.actionFileQuit		.triggered.connect(self.close)
		self.actionSendToExternalSoftware.triggered.connect(
				self.SLOT_actionSendToExternalSoftware)
		self.actionEditPreferences.triggered.connect(
				self.SLOT_actionEditPreferences)

		# Add last file list
		mapper = QtCore.QSignalMapper(self)
		for path,act in zip(self.lastFiles.getValues(),self.actionRecentFilesList):
			act.triggered .connect( mapper.map)
			# short.setContext(QtCore.Qt.WidgetShortcut)
			mapper.setMapping(act, path)
		# mapper.mapped.connect( self.SLOT_actionFileOpen )# TR:todelete
		mapper.mapped[str].connect( self.SLOT_actionFileOpen)

		self.actionViewFullScreen	.triggered.connect(
				self.SLOT_actionViewFullScreen)

		self.actionAboutHelp.triggered.connect(
				self.SLOT_actionAboutHelp)
		self.actionAboutAbout.triggered.connect(
				self.SLOT_actionAboutAbout)

		self.textEdit.textChanged .connect(
				self.SLOT_somethingChanged
				)
		self.textEdit.somethingChanged .connect(
				self.SLOT_somethingChanged
				)

		self.textEdit.typographyModification .connect(
				self.SLOT_typographyModification
				)

		self.textEdit.protectedStyleModification .connect(
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

		menuProfiles = menuDocument.addMenu ( "Profiles" )
		for k,v in list(self.textEdit.actionProfileDict.items()):
			menuProfiles.addAction(v)

		menuDocument.addSeparator ()
		menuDocument.addAction(self.actionFileStats)
		menuDocument.addAction(self.actionFileMetaData)
		menuDocument.addSeparator ()
		menuDocument.addAction(self.actionSendToExternalSoftware)
		menuDocument.addAction(self.textEdit.actionGuessLanguage)



		menuStyle = self.menuBar().addMenu ( "Styles" )
		for id in list(TSManager.dictCharStyle.keys()):
			if id in list(self.textEdit.actionStylesDict.keys()):
				menuStyle.addAction(self.textEdit.actionStylesDict[id])
		menuStyle.addSeparator ()
		for id in list(TSManager.dictBlockStyle.keys()):
			if id in list(self.textEdit.actionStylesDict.keys()):
				menuStyle.addAction(self.textEdit.actionStylesDict[id])
		menuStyle.addSeparator ()
		menuStyle.addAction(self.textEdit.actionInsertImage)
		menuStyle.addSeparator ()
		menuStyle.addAction (self.textEdit.actionResetStyle)


		menuView = self.menuBar().addMenu ( "View" )
		menuView.addAction(self.textEdit.actionZoomIn)
		menuView.addAction(self.textEdit.actionZoomOut)
		menuView.addAction(self.textEdit.actionZoomNormal)
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
			list(self.textEdit.actionStylesDict.values())
		for act in list_actions:
			self.addAction(act)

	################################## SLOTS ##################################
	@QtCore.pyqtSlot()
	def SLOT_actionFileSave(self,force_ask=False):
		"""
		Slot used when saving the current file.
		force_ask : if True, will force asking for the new filepath
		"""
		if self.filepath==None or force_ask:
			filepath = FMTextFileManagement.save_gui_filepath(
					self.get_default_opening_saving_site(),
					self,filter="AthW files (*.athw);; All files (*.*)",
					ext=".athw")
		else:
			filepath = self.filepath
		if filepath :
			filepath=str(filepath)


						### Changed : ProgressBar is instable !

			## progressBar = QtWidgets.QProgressBar(parent=self)
			## progressBar.setMaximum(0)
			## progressBar.setValue(0)
			## # center the widget
			## point = self.geometry().center()
			## point1 = progressBar.geometry().center()
			## progressBar.move(point-point1)
			## # set the window to the correct flag
			## progressBar.setWindowFlags(QtCore.Qt.SplashScreen)
			## progressBar.setWindowModality(QtCore.Qt.WindowModal)
			##
			## progressBar.show()
			##
			## # this class is a very classic thread just to save the file while
			## # displaying the progressBar:
			## class TaskThread(QtCore.QThread):
			## 	taskFinished = QtCore.pyqtSignal()
			## 	def run(self1):
			## 		self.CMD_FileSave(filepath=filepath)
			## 		self1.taskFinished.emit()
			##
			## # What we have to do at the end of the saving
			## def finishing():
			## 	progressBar.close()
			## 	self.actionFileSave.setEnabled(False)
			## 	self.setWindowTitle("AthenaWriter : "+self.filepath)
			## 	tmp,filename = os.path.split(self.filepath)
			## 	self.changeMessageStatusBar("Has saved "+filename)
			## 	self.lastFiles.addFile(self.filepath)
			##
			## self.myLongTask = TaskThread()
			## self.myLongTask.taskFinished.connect(
			## 														finishing)
			##
			## # self.myLongTask.taskFinished.connect(finishing)
			## self.myLongTask.start()

			self.textEdit.setReadOnly(True)
			self.CMD_FileSave(filepath=filepath)
			self.actionFileSave.setEnabled(False)
			self.setWindowTitle("AthenaWriter : "+self.filepath)
			tmp,filename = os.path.split(self.filepath)
			self.changeMessageStatusBar("Has saved "+filename)
			self.lastFiles.update([self.filepath])
			self.textEdit.setReadOnly(False)



	@QtCore.pyqtSlot()
	def SLOT_actionFileSaveAs(self):
		"""
		Slot used when saving as the current file.
		"""
		self.SLOT_actionFileSave(force_ask=True)

	@QtCore.pyqtSlot()
	def SLOT_actionFileNew(self):
		"""
		Slot used when creating a new file.
		"""
		res=self.doSaveDialog()
		if (res != QtWidgets.QMessageBox.Yes) and (res != QtWidgets.QMessageBox.No):
			return False
		self.clean_tmp_files() # we remove the previous tmp files
		self.textEdit.setText("")
		self.filepath=None
		self.metadata=DPMetaData()
		self.setWindowTitle("AthenaWriter : NewFile")
		self.changeMessageStatusBar("Created a new file")

		return True

	@QtCore.pyqtSlot(str)
	@QtCore.pyqtSlot()
	def SLOT_actionFileOpen(self,filepath=None):
		"""
		If filepath==None, it will display the window to search the file
		If filepath==None, it will display the window to search the file
		"""
		res=self.doSaveDialog()
		if (res != QtWidgets.QMessageBox.Yes) and (res != QtWidgets.QMessageBox.No):
			return False
		if filepath==None:
			filepath = FMTextFileManagement.open_gui_filepath(
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
				r = QtWidgets.QMessageBox.question(self,"Non existing file",
					"The file "+filepath+" do not exist. Do you want to "+\
					"create it ?",
					QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)

				if r!= QtWidgets.QMessageBox.Yes:
					return False
				self.filepath = filepath

			self.actionFileSave.setEnabled(False)

			self.setWindowTitle("AthenaWriter : "+self.filepath)
			tmp,filename = os.path.split(filepath)
			self.changeMessageStatusBar("Has opened "+filename)
			self.lastFiles.update([self.filepath])

			return True
		else:
			return False

	@QtCore.pyqtSlot()
	def SLOT_actionFileImport(self,checked=False,filepath=None):
		"""
		If filepath==None, it will display the window to search the file
		"""
		res=self.doSaveDialog()
		if (res != QtWidgets.QMessageBox.Yes) and (res != QtWidgets.QMessageBox.No):
			return False
		if filepath==None:
			extensions = list(DIDict.keys())
			filepath = FMTextFileManagement.open_gui_filepath(parent=self,
				dft_opening_saving_site = self.get_default_opening_saving_site(),
				filter='*.'+ ' *.'.join(extensions))

			# filepath = FMTextFileManagement.open_gui_filepath(
			# 		self.get_default_opening_saving_site(),
			# 		self)
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

	@QtCore.pyqtSlot()
	def SLOT_actionFileExport(self):
		dft_opening_saving_site = self.get_default_opening_saving_site()
		if self.filepath!=None:
			res = DEDialog.getFields(
					dft_opening_saving_site=dft_opening_saving_site,
					default_path = self.filepath,
					source_d = self.metadata,
					)
		else:
			res = DEDialog.getFields(
					dft_opening_saving_site=dft_opening_saving_site,
					source_d = self.metadata,
					)

		if res :
			try :
				res1 = self.CMD_FileExport(**res)
			except IOError as e:
				print(e)
				res1 = False
			if res1:
				msg = "Successfull exportation"
				self.changeMessageStatusBar("Has exported "+res['filepath'])
				dia = QtWidgets.QMessageBox.information (
						self,
						"Exportation" ,
						msg)
			else:
				msg = "Unsuccessfull exportation :\n"
				msg += str(e)
				dia = QtWidgets.QMessageBox.critical (
						self,
						"Exportation" ,
						msg)

		# import TextFormat.TextFormat
		# list_extension = [format.extension for format in FEList]
		# res = QtWidgets.QInputDialog. getItem (self,'Export',
								# 'Format of the exportation:', list_extension)
		# if res[1]:
			# res1 = self.CMD_FileExport(format_name = str(res[0]))
			# if res1:
				# self.changeMessageStatusBar("Has exported "+res1)
				# return True
		# return False


	@QtCore.pyqtSlot()
	def SLOT_actionFileStats(self):
		dialog = DPStatisticsDialog(textedit=self.textEdit,parent=self)
		dialog.show()
	@QtCore.pyqtSlot()
	def SLOT_actionFileMetaData(self,d=None):

		if d== None:
			# constraints_dict = {'language': [TLDico.keys()] }
			d = CMDialog.getValueDict(parent=self,
					constants_manager = self.metadata,
					skip_same_as_init = True
					)
		if d and len(d)>0 :
			self.metadata.update(d)
			if 'language' in list(d.keys()):
				self.textEdit.changeLanguage(
					language_name = str(d['language']),gui=True)


			self.SLOT_somethingChanged()

		# dialog = MDMetaDataDialog(metadata=self.metadata,parent=self)
		# dialog.show()
	@QtCore.pyqtSlot()
	def SLOT_actionViewFullScreen(self):
		if not self.fullScreened:
			self.showFullScreen()
			# self.textEdit.setVerticalScrollBarPolicy(
			# 		QtCore.Qt.ScrollBarAlwaysOff)
			self.menuBar().setHidden(True)
			if AWPreferences['FULLSCREEN_CENTRAL_MAX_SIZE']>0:
				rec = QtWidgets.QApplication.desktop().screenGeometry()
				marg = rec.width()
				marg -= AWPreferences['FULLSCREEN_CENTRAL_MAX_SIZE']
				marg *= .5
				if marg >0:
					self.setContentsMargins ( marg, 0, marg, 0)
				else :
					print("CAUTION : FULLSCREEN_CENTRAL_MAX_SIZE too high")

			self.fullScreened=True
		else :
			self.showNormal()
			self.setContentsMargins ( 0,0,0, 0)
			self.textEdit.setVerticalScrollBarPolicy(
					QtCore.Qt.ScrollBarAsNeeded)
			self.menuBar().setHidden(False)
			self.fullScreened=False

	@QtCore.pyqtSlot()
	def SLOT_actionAboutHelp(self):
		pass

	@QtCore.pyqtSlot()
	def SLOT_actionAboutAbout(self):

		text = AWAbout.split("\n\n")
		text = [' '.join(a.split('\n')) for a in text]
		text = '\n\n'.join(text)
		text = text.strip()
		QtWidgets.QMessageBox.about(self, "About Athena Writer",text)

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
			res = FMTextFileManagement.save(
					str(self.textEdit.toXml()),tmp_filepath)

	@QtCore.pyqtSlot()
	def SLOT_actionSendToExternalSoftware (self):
		# Send the scene to another software (mine is called Antidote and
		# accept only a certain type of encoding).
		path=AWPreferences['EXTERNAL_SOFT_PATH']
		if path=="":
			QtWidgets.QMessageBox.information(self,
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
		FMTextFileManagement.save(text,name, encoding='utf-8-sig', mode='w')
		try:
			s=subprocess.Popen(path+' '+os.path.abspath(name))
		except OSError as e:
			QtWidgets.QMessageBox.critical(self,"Error with external software",
				"Error when sending the file to the external software\n\n"+str(e))
		else:
			res = QtWidgets.QMessageBox.question(self, "External Software Sender",
					"Have you finished to correct the file?",
					QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)


			if (res == QtWidgets.QMessageBox.Yes) :
				text = FMTextFileManagement.open(name, encoding='utf-8-sig', mode='rb')
				self.textEdit.setText(text,type='xml')

	@QtCore.pyqtSlot()
	def SLOT_actionEditPreferences(self):
		d = CLPreferencesDialog.getValueDict(
			dict_preferences = AWDictPreferences,parent=self)
		if d:
			AWOverwritePreferences(d)
			pref_dict , descr_dict = AWPreferencesToDict(skip_same_as_dft=True)

			d = CLPreferencesFiles()
			d.update(other_dict=pref_dict,where='user')
			d.saveConfig(descriptions=descr_dict,where='user')


	def closeEvent(self, event):
		"""Check if we have changed something without saving"""
		res=self.doSaveDialog()
		if (res == QtWidgets.QMessageBox.Yes) or (res == QtWidgets.QMessageBox.No):
			self.lastFiles.saveConfig('user')
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
			return str(AWPreferences['DLT_OPEN_SAVE_SITE'].expanduser())
		else :
			res,tmp=os.path.split(self.filepath)
			return res

	def doSaveDialog(self):
		"""
		Check if there is any modifications and ask if it has to save the file
		if it not the case.
		"""
		if self.actionFileSave.isEnabled():
			res=QtWidgets.QMessageBox.question(
					self,
					"Modification", "Do you want to save the modifications",
					QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | \
					QtWidgets.QMessageBox.Cancel
					)
			if (res == QtWidgets.QMessageBox.Yes):
				self.SLOT_actionFileSave()
			return res
		return QtWidgets.QMessageBox.Yes

	def changeMessageStatusBar(self,message=None):
		"""This function is called to display a message in the status bar"""
		if message==None: message=""
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
