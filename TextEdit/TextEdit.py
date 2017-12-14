from PyQt5 import QtGui, QtCore, QtWidgets

import sys
import shutil
import os

from .TextEditCharTable 				import *
from .TextEditPreferences 				import *
from .TextEditFindReplace 				import *
from .TextEditHighlighter				import *
from TextStyles.TextStyles				import *
from TextStyles.TextStylesList			import TSStyleClassChar,TSStyleClassBlock,TSFontSizeAdjusmentDict
from TextLanguages.TextLanguages		import *
from CommonObjects.CommonObjects		import COOrderedDict
from ConfigLoading.ConfigLoading 		import CLSpelling,CLAutoCorrection
from FileManagement.FileManagement 		import FMTextFileManagement

from TextStyles.TextStylesPreferences			import TSPreferences
from TextLanguages.TextLanguagesPreferences		import TLPreferences

class TETextEdit(QtWidgets.QTextEdit):
	somethingChanged = QtCore.pyqtSignal()
	typographyModification = QtCore.pyqtSignal(object)
	protectedStyleModification = QtCore.pyqtSignal(object)
	def __init__(self, parent=None,language_name=None):
		"""
		- parent : the parent widget
		"""
		QtWidgets.QTextEdit.__init__(self,parent=None)

		self.cursorPositionChanged.connect( self.SLOT_cursorPositionChanged)
		self.textChanged .connect( self.SLOT_textChanged)

		self.setup_actions()
		self.setup_connections()

		self.old_cursor_position=self.textCursor().position() #we will remember
				# the old position of the cursor in order to make typography
				# corrections when it will move

		local_dir = self.get_local_dir()
		self.dict_autocorrection = CLAutoCorrection.get_values(
														local_dir=local_dir)
		self.changeLanguage(language_name)

		self.findDialog 		= TEFindDialog(textedit=self)
		self.charWidgetTable	= TECharWidgetTable(linked_text_widget=self)

		# self.isInsertingSeparator = False #TODO

		# UGLY !!!!
		TSManager.textedit=self



		# Let's set the first zoom
		self.SLOT_defaultZoom()
		self.setText()

	def setup_actions(self):
		Act = QtWidgets.QAction
		self.actionCopy				 		= Act("Copy",self)
		self.actionCut				 		= Act("Cut",self)
		self.actionPaste			 		= Act("Paste",self)
		self.actionUndo				 		= Act("Undo",self)
		self.actionRedo				 		= Act("Redo",self)
		# self.actionChangeLanguage	 		= Act("Change language",self)
		self.actionEnableTypo		 		= Act("Enable typography",self)
		self.actionLaunchCharWidgetTable 	= Act("&Special Characters",self)
		self.actionLaunchFindDialog 		= Act("&Find",self)
		self.actionFindNext			 		= Act("FindNext",self)
		self.actionFindPrevious		 		= Act("FindPrevious",self)
		# self.actionEmphasize			 	= Act("&Emphasize",self)
		# self.actionSeparator			 	= Act("Add/Remove Separator",self)
		self.actionRecheckTypography	 	= Act("&Recheck typography",self)
		self.actionResetStyle				= Act("&Reset Style",self)
		self.actionInsertImage				= Act("&Insert Image",self)
		self.actionGuessLanguage			= Act("Guess Language",self)
		self.actionZoomIn					= Act("Zoom In",self)
		self.actionZoomOut					= Act("Zoom Out",self)
		self.actionZoomNormal				= Act("Reset Zoom",self)

		self.actionProfileDict				= COOrderedDict()
		self.actionProfileDict[0]=Act("Strict profile",self) # profile = 0
		self.actionProfileDict[1]=Act("Medium profile",self) # profile = 1
		self.actionProfileDict[10]=Act("Loose profile",self) # profile = 10
		actionProfileGroup = QtWidgets.QActionGroup(self)
		for act in self.actionProfileDict.values():
			actionProfileGroup.addAction(act)
			act.setCheckable(True)




		KS = QtGui.QKeySequence
		self.actionCopy				 		.setShortcuts(KS.Copy		)
		self.actionCut				 		.setShortcuts(KS.Cut		)
		self.actionPaste			 		.setShortcuts(KS.Paste		)
		self.actionUndo				 		.setShortcuts(KS.Undo		)
		self.actionRedo				 		.setShortcuts(KS.Redo		)
		# self.actionEmphasize		 		.setShortcuts(KS("Ctrl+E")	)
		# self.actionSeparator		 		.setShortcuts(KS("Ctrl+K")	)
		# self.actionChangeLanguage	 		.setShortcuts(KS.ChangeLanguage	 	   )
		# self.actionEnableTypo		 		.setShortcuts(KS.EnableTypo		 	   )
		# self.actionLaunchCharWidgetTable 	.setShortcuts(KS.LaunchCharWidgetTable )
		self.actionLaunchFindDialog	 	    .setShortcuts(KS.Find )
		self.actionFindNext			 	    .setShortcuts(KS.FindNext )
		self.actionFindPrevious		 	    .setShortcuts(KS.FindPrevious )
		self.actionFindPrevious		 	    .setShortcuts(KS.FindPrevious )
		# self.actionResetFormat		 	    .setShortcuts(KS.FindPrevious )
		# self.actionZoomIn		 	    	.setShortcuts(KS("Ctrl+D") )
		# self.actionZoomOut		 	    	.setShortcuts(KS("Ctrl+M") )
		self.actionZoomNormal		 	    .setShortcuts(KS("Ctrl+0") )


		self.actionStylesDict = COOrderedDict()
		charActionGroup = QtWidgets.QActionGroup(self)
		blockActionGroup = QtWidgets.QActionGroup(self)
		for style in TSManager.listCharStyle + TSManager.listBlockStyle :
			if not isinstance(style,TSStyleClassImage):
				if style.name!="":
					act = QtWidgets.QAction(style.name,self)
				else:
					act = QtWidgets.QAction(style.xmlMark,self)
				if style.shortcut!=None:
					act.setShortcuts(QtGui.QKeySequence(style.shortcut))

				self.actionStylesDict[style.userPropertyId] = act
				if style in TSManager.listCharStyle:
					charActionGroup.addAction(act)
				elif style in TSManager.listBlockStyle:
					blockActionGroup.addAction(act)
				act.setCheckable(True)


	def setup_connections(self):



		self.actionCopy.triggered.connect(self.copy)
		self.actionCut.triggered.connect(self.cut)
		self.actionPaste.triggered.connect(self.paste)
		self.actionUndo.triggered.connect(self.undo)
		self.actionRedo.triggered.connect(self.redo)
		# self.actionEnableTypo.triggered.connect(self.SLOT_actionEnableTypo	)
		self.actionLaunchCharWidgetTable.triggered.connect(
										self.SLOT_actionLaunchCharWidgetTable)
		self.actionLaunchFindDialog.triggered.connect( self.SLOT_actionLaunchFindDialog)
		self.actionFindNext.triggered.connect(self.SLOT_actionFindNext)
		self.actionFindPrevious.triggered.connect(self.SLOT_actionFindPrevious)
		# self.actionEmphasize.triggered.connect(self.SLOT_actionEmphasize)
		# self.actionSeparator.triggered.connect(self.SLOT_actionSeparator)
		self.actionRecheckTypography.triggered.connect(self.SLOT_actionRecheckTypography)
		self.actionResetStyle.triggered.connect(self.SLOT_actionResetStyle)
		self.actionInsertImage.triggered.connect(self.SLOT_actionInsertImage)
		self.actionGuessLanguage.triggered.connect(self.SLOT_actionGuessLanguage)
		self.actionZoomIn.triggered.connect(lambda  : self.zoomIn(TEPreferences["ZOOM_INCREMENT"]))
		self.actionZoomOut.triggered.connect(lambda  : self.zoomOut(TEPreferences["ZOOM_INCREMENT"]))
		self.actionZoomNormal.triggered.connect(self.SLOT_defaultZoom)

		# add the formatting (emphasize, set tot tile etc.) shortcuts to the
		mapper = QtCore.QSignalMapper(self)
		for userPropertyId,act in list(self.actionStylesDict.items()):
			act.triggered.connect( mapper.map)
			mapper.setMapping(act, userPropertyId)
		# mapper.mapped.connect( self.SLOT_setStyle) # TR:todelete
		mapper.mapped[int].connect( self.SLOT_setStyle)

		# add the profiles
		mapper = QtCore.QSignalMapper(self)
		for i,act in list(self.actionProfileDict.items()):
			act.triggered.connect( mapper.map)
			mapper.setMapping(act, i)
		# mapper.mapped.connect( self.SLOT_changeProfile) # TR:todelete
		mapper.mapped[int].connect( self.SLOT_changeProfile)



	def get_local_dir(self):
		"""Will rteturn the local dir of the AWMainWindow in order to search
		for additional spelling words or autocorrection."""
		if self.parent()== None or self.parent().filepath==None:
			local_dir = None
		else:
			local_dir,tmp = os.path.split(self.parent().filepath)
		return local_dir

	def setText(self,text=None,new_language=None,type='plain',profile=None):
		"""This method will set the text contained in text (when changing the
		active scene for instance.
		- text : the text to insert (if None then it will insert u"")
		- new_language : the language of the text, if it is None, we keep the
				previous one
		- type : 'plain' if raw text ; 'xml' if the personal format ; 'html' if
				html
		"""
		if text==None: text=""
		for k,v in TEDictCharReplace.items():
			text = text.replace(k,v)
		# We change the language if necessary
		if new_language!=None :
			if self.language.name!=new_language or self.language.profile!=profile:
				self.changeLanguage(new_language,profile=profile)

		# Creating the new document with the good default format and inserting
		# the text in it
		document=QtGui.QTextDocument(self)
		cursor , document= self.setDocumentFormat(document)
		local_dir = self.get_local_dir()

		self.dict_autocorrection = CLAutoCorrection.get_values(
														local_dir=local_dir)
		if TEPreferences['SPELL_CHECK'] and TEHasEnchant :
			list_spelling = CLSpelling.get_values(local_dir=local_dir)
			self.highlighter = TEHighlighter(document,self.language,
												list_spelling=list_spelling)


		if type=='plain' 	: cursor.insertText(text)
		elif type=='html' 	: cursor.insertHtml (text)
		elif type=='xml' 	:
			cursor.insertText(text)
			TSManager.fromXml(document)
		cursor.setPosition(0)

		# Recheck the document typography if necessary
		if TEPreferences["RECHECK_TEXT_OPEN"]:
			self.language.cheak_after_paste(cursor)

		self.blockSignals (True)
		self.setDocument(document)
		# When you set a new document, for some reason, it lost the zoom
		# just a small  In and Out and it reset the zoom
		self.zoomIn(1)
		self.zoomOut(1)

		self.document().clearUndoRedoStacks() # It will empty the history (no
															# "undo" before)
		self.blockSignals (False)
		self.setTextCursor(cursor)



	################################# SLOTS ###################################

	def SLOT_cursorPositionChanged(self):
		"""Method that is called when the cursor position has just changed."""
		self.blockSignals (True) #allow the method to move the cursor in the
									# method without calling itself once again.

		if self.old_cursor_position>=self.document().characterCount():
			# If we were at the end of the document and suppress the end, it
			# does then nothing.
			self.old_cursor_position=self.textCursor().position()
			self.blockSignals (False)
			return self.old_cursor_position



		modification = False
		if TEPreferences["AUTO_CORRECTION"]:
			# If we have just written a word (by a space, or a ponctuation) it
			# makes the auto-correction of the word.
			cursor=self.textCursor()
			cursor.beginEditBlock()
			last_char=self.language.lastChar(cursor)
			list_word_break = [' ','\u00A0','\n',';',':','!','?',',',
					'.',"'",'-']
			list_word_break = [TEDictCharReplace.get(s,s) for s in
															list_word_break]
			if last_char in list_word_break:
				# if we just finished writting a word
				position_0 = cursor.position()
				replace = self.language.afterWordWritten(cursor)
				if replace :
					# We update the position in order to make the good
					# typography correction just afterwards
					position_gap = self.textCursor().position()-position_0
					self.old_cursor_position += position_gap # we move the
								# previous position from the corresponding gap
					assert 0<= self.old_cursor_position <\
							self.document().characterCount()
			cursor.endEditBlock()


		if TEPreferences["DO_TYPOGRAPHY"]:
			# We check the typography at the site we just left
			cursor=QtGui.QTextCursor(self.document())
			cursor.clearSelection()
			cursor.setPosition(self.old_cursor_position)
			cursor.beginEditBlock()
			modification=self.language.correct_between_chars(cursor)

			# i=0
			# while modification and i<TEPreferences["LIM_RECURSIV_UNDO"]:
			# 	modification=self.language.correct_between_chars(cursor)
			# 	if i>1:
			# 		print("modification",modification)
			# 	i+=1
			# 	if i==TEPreferences["LIM_RECURSIV_UNDO"]:
			# 		print ("Reach LIM_RECURSIV_UNDO in "
			# 				"SLOT_cursorPositionChanged")
			cursor.endEditBlock()


		self.blockSignals (False)
		if modification:
			self.typographyModification .emit(
					modification)

		self.old_cursor_position=self.textCursor().position() #update the
															# cursor position
		self.checkStyleAction()

		return self.old_cursor_position

	def SLOT_textChanged(self):
		block_id = self.textCursor().blockFormat().property(
												QtGui.QTextFormat.UserProperty)
		# # block_id = block_id.toPyObject()
		if block_id!=None and TSManager.dictStyle[block_id].protected :
			self.blockSignals (True)
			self.undo()
			self.blockSignals (False)
			self.protectedStyleModification .emit(
				"Try to modify a protected block (use Ctrl+L to delete it).")
		self.checkStyleAction()

		# To avoid a strange bug: when suppressing everything, it tends to reset
		# the font.
		if block_id==None and self.document().isEmpty():
			if "defaultCharFormat" in self.__dict__:
				self.setCurrentCharFormat(self.defaultCharFormat)


	def SLOT_pluggins(self,iterator):
		"""Launch the pluggin corresponding to the iterator"""
		function=self.dico_pluggins[iterator]
		function(cursor=self.textCursor())


	@QtCore.pyqtSlot()
	def SLOT_actionLaunchCharWidgetTable(self):
		"""Slot that is called when we have to display the char table"""
		self.charWidgetTable.setVisible(True)

	@QtCore.pyqtSlot()
	def SLOT_actionLaunchFindDialog(self):
		"""Slot that is called when we have to display the search dialog
		window."""
		self.findDialog.setVisible(True)

	@QtCore.pyqtSlot()
	def SLOT_actionFindNext	(self):
		"""Slot that is called when we have to display the next occurence of
		the search dialog window"""
		self.findDialog.activate_next()

	@QtCore.pyqtSlot()
	def SLOT_actionFindPrevious	(self):
		"""Slot that is called when we have to display the previous occurence
		of the search dialog window"""
		self.findDialog.activate_previous()

	@QtCore.pyqtSlot()
	def SLOT_actionRecheckTypography(self,ask=False):
		"""Quick method that check and correct all the typography of the text.
		TODO : some summuary window of all the corrections.
		if ask, will ask fot the check of typography
		"""
		if ask:
			r = QtWidgets.QMessageBox.question(self, "Recheck Typography",
				"Do you want to import the recheck the typography ?",
				QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
			if r== QtWidgets.QMessageBox.No:
				return False
		cursor=self.textCursor()
		cursor.setPosition(0)
		self.language.cheak_after_paste(cursor)

	def SLOT_correctWord(self,word):
		"""
		Replaces the selected text with word.
		"""
		cursor = self.textCursor()
		cursor.beginEditBlock()

		cursor.removeSelectedText()
		cursor.insertText(word)

		self.language.cheak_after_paste(cursor,len(word) )

		cursor.endEditBlock()


	def SLOT_addWordSpelling(self,word,where='local'):
		"""
		Add the word into the configuration file of the spelling
		"""
		# to replace curved apostroph by stright ones
		word = self.highlighter.toRawWord(word)
		local_dir = self.get_local_dir()

		try :
			CLSpelling.add_words(words=[word],where=where,local_dir=local_dir)
			self.highlighter.dict.add(word)
			self.highlighter.rehighlight ()

		except IOError as e:
			QtWidgets.QMessageBox.critical(self,'Input error',e)

	def SLOT_setStyle(self,style_id):
		cursor=self.textCursor()
		cursor.beginEditBlock()
		self.blockSignals (True)
		TSManager.inverseStyle(cursor,style_id)
		cursor.endEditBlock()
		self.setTextCursor(cursor)
		self.blockSignals (False)
		self.checkStyleAction()
		self.somethingChanged .emit()

	@QtCore.pyqtSlot()
	def SLOT_actionResetStyle(self):
		cursor=self.textCursor()
		cursor.beginEditBlock()
		self.blockSignals (True)
		try:
			TSManager.resetStyle(cursor)
		finally:
			self.blockSignals (False)
			cursor.endEditBlock()
		self.somethingChanged .emit()

	@QtCore.pyqtSlot()
	def SLOT_actionInsertImage(self):
		if self.parent()!=None:
			dft_opening_site = self.parent().get_default_opening_saving_site()
			local_dir = self.get_local_dir()
		else:
			dft_opening_site ='.'
			local_dir = False
		filepath = FMTextFileManagement.open_gui_filepath(
					dft_opening_site ,
					self,filter="Image Files (*.png *.jpg *.bmp *.gif)")

		if filepath:
			d,f = os.path.split(filepath)
			assert os.path.isabs(d)

			if local_dir and d!=os.path.abspath(local_dir):
				assert os.path.isabs(local_dir)
				r = QtWidgets.QMessageBox.question(self, "Local importation",
					"Do you want to import the file locally ?",
					QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
				if r== QtWidgets.QMessageBox.Yes:
					newfilepath = os.path.join(local_dir,f)
					newfilepath = FMTextFileManagement.exists(newfilepath)
					if not newfilepath:
						return False
					shutil.copyfile(filepath,newfilepath)
					tmp,newfilepath = os.path.split(newfilepath) #local path
			elif not local_dir:
				newfilepath = filepath
				r = QtWidgets.QMessageBox.question(self, "Local importation",
					"Since you did not saved the file, the absolute path "+\
					"will be displayed. For import the file localy, save "+\
					"first",
					QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.Cancel)
				if r== QtWidgets.QMessageBox.Cancel:
					return False
			else :
				tmp,newfilepath = os.path.split(filepath)	#local path

			# self.SLOT_setFormating(TSStyleImage.userPropertyId)
			self.blockSignals(True)

			cursor=self.textCursor()
			cursor.clearSelection()
			block_id = cursor.blockFormat().property(
												QtGui.QTextFormat.UserProperty)
			# # block_id = block_id.toPyObject()
			if block_id==TSStyleImage.userPropertyId :
				# if there is an image, we remove the previous one
				TSManager.inverseStyle(cursor,block_id)
			TSManager.inverseStyle(cursor,TSStyleImage.userPropertyId)
			cursor.beginEditBlock()
			cursor.insertText(newfilepath)
			cursor.endEditBlock()
			self.blockSignals(False)
			self.somethingChanged .emit()

			return filepath
		return False

	@QtCore.pyqtSlot()
	def SLOT_actionGuessLanguage(self):
		v = TLGuessLanguages(self.toPlainText())
		r = QtWidgets.QMessageBox.question(self, "Guess Language",
				"The new language detected is "+v+"; change the language?",
				QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		if r== QtWidgets.QMessageBox.Yes:
			if self.parent()!=None:
				self.parent().metadata.update({"language":v})
			self.changeLanguage(v,gui=True)



	def SLOT_changeProfile(self,i):
		old_i = self.language.profile
		self.language.profile = i
		self.actionStylesDict[i].setEnabled(True)
		# self.setProfileEnabled()

		if i < old_i:
			self.SLOT_actionRecheckTypography(ask=True)
		self.somethingChanged .emit()

	def SLOT_defaultZoom(self):
		f = self.document().defaultFont().pointSize()
		self.zoom(TEPreferences['ZOOM_DEFAULT']-f)

	def resizeEvent(self,event):
		QtWidgets.QTextEdit.resizeEvent(self,event)
		self.ensureCursorVisible()

	def insertFromMimeData(self,source ):
		"""A re-implementation of insertFromMimeData. We have to check the
		typography of what we have just paste.
		TODO : some summary window of all the corrections.
		"""
		self.blockSignals (True)
		cursor=self.textCursor()
		cursor.beginEditBlock()
		cursor_pos=cursor.position()
		if source.hasFormat("text/athena"):
			xml = source.data("text/athena")
			# 106 for the utf-8
			xml = QtCore.QTextCodec.codecForMib(106).toUnicode(xml)
			document = QtGui.QTextDocument()
			document.setPlainText(xml)
			TSManager.fromXml(document)
			cur = QtGui.QTextCursor(document)
			cur.select(QtGui.QTextCursor.Document)
			sel = cur.selection()
			cursor.insertFragment(cur.selection())
			size = len(sel.toPlainText())

		# if source.html()==self.lastCopy[0].html():
		# 	# if the pasted thing comes from the document itself
		# 	cursor.insertFragment(self.lastCopy[1])
		# 	size = len(self.lastCopy[1].toPlainText())
		else :
			text=source.text()
			text.replace("\t", " ")
			for k,v in TEDictCharReplace.items():
				text = text.replace(k,v)
			cursor.insertText(text)
			size = len(text)

		cursor.setPosition(cursor_pos)
		if TEPreferences["DO_TYPOGRAPHY"]:
			self.language.cheak_after_paste(cursor,size)
		cursor.setPosition(cursor_pos)
		cursor.movePosition(
				QtGui.QTextCursor.Right,
				QtGui.QTextCursor.KeepAnchor,
				n = size)
		# self.setTextCursor(cursor)
		TSManager.recheckBlockStyle(cursor)
		TSManager.recheckCharStyle(cursor)
		cursor.endEditBlock()
		self.blockSignals (False)


	def createMimeDataFromSelection(self):
		selection = self.textCursor().selection()

		mimeData = QtWidgets.QTextEdit.createMimeDataFromSelection(self)
		# Base mime data: create a temporary textedit (not very clean)
		te = QtWidgets.QTextEdit()
		document=te.document()
		QtGui.QTextCursor(document).insertFragment(selection)

		for k,v in TEDictCharReplace.items(): # replace the non-breakable spaces
			cursor = document.find(v)
			while not cursor.isNull():
				cursor.insertText(k)
				cursor = document.find(v,cursor.position()+1)
		cursor = QtGui.QTextCursor(document)
		cursor.select(QtGui.QTextCursor.Document)
		te.setTextCursor(cursor)
		mimeData = te.createMimeDataFromSelection()

		# Athena Writer XML we create a temporary document
		document=QtGui.QTextDocument()
		QtGui.QTextCursor(document).insertFragment(selection)

		# We create the  corresponding xml data
		data = TSManager.toXml(document)
		# mimeData = QtCore.QMimeData()
		mimeData.setData("text/athena", data.encode('utf-8'))
		mimeData.text() # For some reason, needs to call text in order to update the formats
		return mimeData

	def changeLanguage(self,language_name=None,profile=None,gui=False):
		"""
		- language_name: the name of the language, should be in TLDico.keys()
		- profile: the typography profile to use for the document
		- gui: if true, will propose to check the typography is the document is
			not empty
		"""
		print(('TO CHECK : we indeed changed the local dir before changing '+\
			'the language.'))
		local_dir = self.get_local_dir()
		# fill self.language according to the language in entry
		if language_name==None:
			lang = TLDico[TLPreferences["DFT_WRITING_LANGUAGE"]]
			self.language=lang(self.dict_autocorrection,profile=profile)
		else :
			# FUTURE to change  merge TLDico and choice
			if str(language_name) not in TLDico:
				lang = TLDico[TLPreferences["DFT_WRITING_LANGUAGE"]]
				self.language=lang(self.dict_autocorrection,profile=profile)
				raise WWError("Do not have the typography for the language "+\
																language_name)
			else:
				lang = TLDico[language_name]
				self.language = lang(self.dict_autocorrection,profile=profile)
				profile = self.language.profile

		self.actionProfileDict[self.language.profile].setChecked(True)

		## PROBLEM IF WE CHANGE OF LANGUAGE, WE KEEP THE OLD PLUGGINS
		# add the language insert shortcuts to the class
		dico = self.language.shortcuts_insert
		mapper = QtCore.QSignalMapper(self)
		for k in list(dico.keys()):
			short=QtWidgets.QShortcut(QtGui.QKeySequence(*k),self)
			short.activated .connect( mapper.map)
			short.setContext(QtCore.Qt.WidgetShortcut)
			mapper.setMapping(short, dico[k])
		# mapper.mapped.connect( self.insertPlainText ) # TR:todelete
		mapper.mapped[str].connect( self.insertPlainText)

		# add the language pluggins to the class
		dico=self.language.shortcuts_correction_plugins
		self.dico_pluggins={}
		mapper = QtCore.QSignalMapper(self)
		for i,k in enumerate(dico.keys()):
			short=QtWidgets.QShortcut(QtGui.QKeySequence(*k),self)
			short.activated .connect( mapper.map)
			short.setContext(QtCore.Qt.WidgetShortcut)

			self.dico_pluggins[i]=dico[k]
			mapper.setMapping(short, i)
		# mapper.mapped.connect( self.SLOT_pluggins )# TR:todelete
		mapper.mapped[int].connect( self.SLOT_pluggins)

		# Change the Highlighter for the new language
		if TEPreferences['SPELL_CHECK'] and TEHasEnchant :
			if local_dir!=None:
				list_spelling = CLSpelling.get_values(local_dir=local_dir)
			else:
				list_spelling=None
			self.highlighter = TEHighlighter(self.document(),self.language,
												list_spelling=list_spelling)
			self.highlighter.rehighlight ()

		if gui and not self.document().isEmpty():
			self.SLOT_actionRecheckTypography(ask=True)

	def undo(self):
		"""
		This method do the usual undo, except in the case it has there has be a
		typography correction, in which case it comes back to the state before
		the events that trigger the correction:
		exemple:
		"Hello you.."
			-----     add dot     		----->       "Hello you..."
			----- typography correction ----->       "Hello you…"
			-----        Ctrl-Z         ----->       "Hello you..."

		"""
		self.blockSignals (True)
		if TEPreferences["DO_TYPOGRAPHY"]:
			i=1
			do_again=True
			while do_again and i<TEPreferences["LIM_RECURSIV_UNDO"]:
				for j in range(i):
					QtWidgets.QTextEdit.undo(self)
				cursor=self.textCursor()
				cursor.clearSelection()
				do_again=self.language.correct_between_chars(cursor)
				i+=1
			if i==TEPreferences["LIM_RECURSIV_UNDO"]:
				print("Reach LIM_RECURSIV_UNDO in undo")
			self.old_cursor_position = self.textCursor().position() # update
					# the cursor position
		else:
			QtWidgets.QTextEdit.undo(self)
		self.blockSignals (False)


	def keyPressEvent(self,event):
		"""
		This action grab the Undo KeySequence to execute the special function
		self.undo, self.copy, self.cut.
		"""
		if (event.matches(QtGui.QKeySequence.Undo)):
			self.undo()
		elif (event.matches(QtGui.QKeySequence.Redo)):
			self.redo()
		elif (event.matches(QtGui.QKeySequence.Copy)):
			self.copy()
		elif (event.matches(QtGui.QKeySequence.Cut)):
			self.cut()
		elif (event.key() == QtCore.Qt.Key_Tab):
			pass # No tab…
		elif (event.key() == QtCore.Qt.Key_Alt):
			# if self.parent()!=None:
			# 	self.parent().keyPressEvent(event)
		else:
			QtWidgets.QTextEdit.keyPressEvent(self,event)



	def toPlainText(self):
		"""
		Re-implementation of toplaintext in order to have the inbrekable spaces
		(for an unkown reason it is not suported by the QTextEdit.toPlainText
		function).
		"""
		cursor = QtGui.QTextCursor(self.document())
		cursor.select(QtGui.QTextCursor.Document)
		s = str(cursor.selectedText())
		s = s.replace('\u2029','\n')
		return s


	def toXml(self):
		newText=TSManager.toXml(self.document())
		for k,v in TEDictCharReplace.items():
			newText = newText.replace(v,k)
		return newText

	def contextMenuEvent(self, event):
		cursor = QtGui.QTextCursor(self.document())
		cursor = self.cursorForPosition(event.pos())
		self.setTextCursor(cursor)

		popup_menu = QtWidgets.QMenu(self)


		if TEPreferences['SPELL_CHECK'] and TEHasEnchant:
			# Select the word under the cursor.
			cursor = self.textCursor()
			cursor.select(QtGui.QTextCursor.WordUnderCursor)
			self.setTextCursor(cursor)

			# Check if the selected word is misspelled and offer spelling
			# suggestions if it is.
			if self.textCursor().hasSelection():
				text = str(self.textCursor().selectedText())
				text = self.highlighter.toRawWord(text)
				if not self.highlighter.dict.check(text):
					spell_menu = QtWidgets.QMenu('Spelling Suggestions')

					# Add wordcorrection to the mapper
					mapper = QtCore.QSignalMapper(self)
					for word in self.highlighter.dict.suggest(text):
						act = QtWidgets.QAction(word, spell_menu)

						act.triggered .connect( mapper.map)
						mapper.setMapping(act, word)
						spell_menu.addAction(act)

					# mapper.mapped.connect( self.SLOT_correctWord )# TR:todelete
					mapper.mapped[str].connect( self.SLOT_correctWord)

					# Only add the spelling suggests to the menu if there are
					# suggestions.
					if len(spell_menu.actions()) != 0:
						spell_menu.addSeparator()
						act_loc = QtWidgets.QAction('Add word to local dict',
																	spell_menu)
						act_usr = QtWidgets.QAction('Add word to user dict',
																	spell_menu)
						act_glo = QtWidgets.QAction('Add word to global dict',
																	spell_menu)

						spell_menu.addAction(act_loc)
						spell_menu.addAction(act_usr)
						spell_menu.addAction(act_glo)

						if self.parent()==None or self.parent().filepath==None:
							act_loc.setEnabled(False)

						# c = QtCore.QObject.connect # TR:todelete
						# trig = QtCore.SIGNAL("triggered ()")# TR:todelete

						slot_loc = lambda : self.SLOT_addWordSpelling(text,'local')
						slot_usr = lambda : self.SLOT_addWordSpelling(text,'user')
						slot_glo = lambda : self.SLOT_addWordSpelling(text,'global')

						act_loc.triggered.connect( slot_loc)
						act_usr.triggered.connect( slot_usr)
						act_glo.triggered.connect( slot_glo)

						# map = QtCore.SLOT("map()")
						# act_loc.triggered.connect( mapper, map)
						# mapper.setMapping(act, text,'local'))
						# act_usr.triggered.connect( mapper, map)
						# mapper.setMapping(act, text))
						# act_glo.triggered.connect( mapper, map)
						# mapper.setMapping(act, text))


						# self.connect(
							# mapper,
							# QtCore.SIGNAL("mapped(const QString &)"),
							# self.SLOT_addWordSpelling
							# )

						popup_menu.addSeparator()
						popup_menu.addMenu(spell_menu)

		popup_menu.addAction(self.actionUndo)
		popup_menu.addAction(self.actionRedo)
		popup_menu.addSeparator()
		popup_menu.addAction(self.actionCut)
		popup_menu.addAction(self.actionCopy)
		popup_menu.addAction(self.actionPaste)

		popup_menu.exec_(event.globalPos())

	def setDocumentFormat(self,document):
		if "alignment" in TSPreferences['DEFAULT_STYLE']:

			align_name = TSPreferences['DEFAULT_STYLE']["alignment"]
			if align_name in TSStyleClassBlock.dict_align:
				obt=QtGui.QTextOption(TSStyleClassBlock.dict_align[align_name])
				document.setDefaultTextOption(obt)
			else :
				KeyError('Unknown key for the alignement : '+align_name)

		cursor=QtGui.QTextCursor(document)
		format_block=cursor.blockFormat()


		if TEPreferences['TEXT_INDENT']>0:
			format_block.setTextIndent (TEPreferences['TEXT_INDENT'])

		if TEPreferences['TEXT_LINE_HEIGHT']>0:
			format_block.setLineHeight (TEPreferences['TEXT_LINE_HEIGHT'],
									QtGui.QTextBlockFormat.ProportionalHeight)

		if TEPreferences['TEXT_MARGIN']>0:
			document.setDocumentMargin(TEPreferences['TEXT_MARGIN'])

		# Putting the cursor at the good format
		cursor.setBlockFormat(format_block)

		self.defaultBlockFormat = format_block
		self.defaultCharFormat = cursor.charFormat()
		if "font_name" in TSPreferences['DEFAULT_STYLE']:
			self.defaultCharFormat.setFontFamily(
								TSPreferences['DEFAULT_STYLE']["font_name"])
		if "font_size" in TSPreferences['DEFAULT_STYLE']:
			v = TSFontSizeAdjusmentDict[TSPreferences['DEFAULT_STYLE']["font_size"]]
			self.defaultCharFormat.setProperty(
									QtGui.QTextFormat.FontSizeAdjustment,v)
		cursor.setCharFormat(self.defaultCharFormat)


		return cursor,document

	def emit_typographyModification(self):
		self.typographyModification .emit()

	def checkStyleAction(self):
		"""Check whenether the action of the styles should be checked or not"""
		# Enable the good action in the styles
		cursor = self.textCursor()
		charId = cursor.charFormat().property(QtGui.QTextFormat.UserProperty)
		blockId = cursor.blockFormat().property(QtGui.QTextFormat.UserProperty)
		for id,act in self.actionStylesDict.items():
			if id in {charId,blockId}:
				act.setChecked(True)
			else:
				act.setChecked(False)

	def zoom(self,range=3):
		"""
		usefull discussion
		https://stackoverflow.com/questions/8016530/no-effect-from-zoomin-in-qtextedit-after-font-size-change
		"""

		if range>0:
			self.zoomIn(range=range)
		elif range<0:
			self.zoomOut(range=-range)



	def wheelEvent(self, event):
		if (event.modifiers() & QtCore.Qt.ControlModifier):
			# (1, -1)[x < 0] elegant way to have sign
			sign = lambda x : (x>0)-(x<0)
			self.zoom(sign(event.angleDelta().y())*TEPreferences["ZOOM_INCREMENT"])
		else:
			QtWidgets.QTextEdit.wheelEvent(self, event)


if __name__ == '__main__':

	import sys

	app = QtWidgets.QApplication(sys.argv)

	textedit = TETextEdit(language_name='French',parent=None)
	# button_refresh	 	= QtWidgets.QPushButton('Stupidity')
	# textedit.connect(textedit,QtCore.SIGNAL('typographyModification ()'), stupidity)
	# textedit.emit_typographyModification()
	# button_refresh.clicked .connect( textedit.toPlainText1)
	# textedit.typographyModification.connect(stupidity)
	textedit.show()
	# button_refresh.show()


	sys.exit(app.exec_())
