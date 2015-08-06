from PyQt4 import QtGui, QtCore

import sys
import string
import shutil

from TextEditLanguages 					import *
from TextEditCharTable 					import *
from TextEditConstants 					import *
from TextEditFindReplace 				import *
from TextEditHighlighter				import *
from TextStyles.TextStyles				import *
from TextStyles.TextStylesConstants		import TSConstants
from ConfigLoading.ConfigLoading 		import CLSpelling,CLAutoCorrection
from FileManagement.FileManagement 		import FMFileManagement

class TETextEdit(QtGui.QTextEdit):
	def __init__(self, parent=None,language_name=None,local_dir=None,
					font_indent=False,font_line_height=False,doc_margin=False):
		"""
		- parent : the parent widget
		- local_dir : a local directory where to find some config files
			(spelling, autcor).
		"""
		QtGui.QTextEdit.__init__(self,parent=None)

		self.font_indent        = font_indent
		self.font_line_height   = font_line_height
		self.doc_margin			= doc_margin
		self.local_dir			= local_dir #usefull to save the file
		
		QtCore.QObject.connect(self,QtCore.SIGNAL("cursorPositionChanged()"),
											self.SLOT_cursorPositionChanged)
		QtCore.QObject.connect(self,QtCore.SIGNAL("textChanged ()"),
											self.SLOT_textChanged)
		
		self.old_cursor_position=self.textCursor().position() #we will remember 
				# the old position of the cursor in order to make typography 
				# corrections when it will move
		
		 
		self.dict_autocorrection = CLAutoCorrection.get_values(
														local_dir=local_dir)
		self.changeLanguage(language_name,local_dir=local_dir) # redo a version where we do not need to send local_dir
		
		self.findDialog 		= TEFindDialog(textedit=self)
		self.charWidgetTable	= TECharWidgetTable(linked_text_widget=self)
		
		# self.isInsertingSeparator = False #TODO

		self.setup_actions()
		self.setup_connections()
		self.setText()
		
		# UGLY !!!!
		TSManager.textedit=self
		
		self.lastCopy = (QtCore.QMimeData(),QtGui.QTextDocumentFragment ())
		
		
			
		
		
	def setup_actions(self):
		Act = QtGui.QAction
		self.actionCopy				 		= Act("Copy",self)
		self.actionCut				 		= Act("Cut",self)
		self.actionPaste			 		= Act("Paste",self)
		self.actionUndo				 		= Act("Undo",self)
		self.actionRedo				 		= Act("Redo",self)
		self.actionChangeLanguage	 		= Act("Change language",self)
		self.actionEnableTypo		 		= Act("Enable typography",self)
		self.actionLaunchCharWidgetTable 	= Act("&Special Characters",self)
		self.actionLaunchFindDialog 		= Act("&Find",self)
		self.actionFindNext			 		= Act("FindNext",self)
		self.actionFindPrevious		 		= Act("FindPrevious",self)
		# self.actionEmphasize			 	= Act("&Emphasize",self)
		# self.actionSeparator			 	= Act("Add/Remove Separator",self)
		self.actionRecheckTypography	 	= Act("&Recheck typography",self)
		self.actionResetFormat				= Act("&Reset format",self)
		self.actionInsertImage				= Act("&InsertImage",self)
		
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
		# self.actionResetFormat		 	    .setShortcuts(KS.FindPrevious )	
		
		
		self.actionFormatsDict = {}
		for format in TSManager.listCharStyle + TSManager.listBlockStyle :
			if not isinstance(format,TSStyleClassImage):
				if format.name!="":
					act = QtGui.QAction(format.name,self)
				else:
					act = QtGui.QAction(format.xmlMark,self)
				if format.shortcut!=None:
					act.setShortcuts(QtGui.QKeySequence(format.shortcut))
				
				self.actionFormatsDict[format.userPropertyId] = act
		
		
		
	def setup_connections(self):
		
		trig = QtCore.SIGNAL("triggered()")
		c = self.connect
		c(self.actionCopy, trig,self.copy)
		c(self.actionCut, trig,self.cut)
		c(self.actionPaste, trig,self.paste)
		c(self.actionUndo, trig,self.undo)
		c(self.actionRedo, trig,self.redo)
		c(self.actionChangeLanguage, trig,self.SLOT_actionChangeLanguage	)
		# c(self.actionEnableTypo, trig,self.SLOT_actionEnableTypo	)
		c(self.actionLaunchCharWidgetTable, trig,
										self.SLOT_actionLaunchCharWidgetTable)
		c(self.actionLaunchFindDialog, trig, self.SLOT_actionLaunchFindDialog)
		c(self.actionFindNext, trig,self.SLOT_actionFindNext)
		c(self.actionFindPrevious, trig,self.SLOT_actionFindPrevious)
		# c(self.actionEmphasize, trig,self.SLOT_actionEmphasize)
		# c(self.actionSeparator, trig,self.SLOT_actionSeparator)
		c(self.actionRecheckTypography, trig,self.SLOT_actionRecheckTypography)
		c(self.actionResetFormat, trig,self.SLOT_actionResetFormat)
		c(self.actionInsertImage, trig,self.SLOT_actionInsertImage)
		
		
		# add the formatting (emphasize, set tot tile etc.) shortcuts to the 
		mapper = QtCore.QSignalMapper(self)
		for userPropertyId,act in self.actionFormatsDict.items():
			c(act,trig, mapper, QtCore.SLOT("map()"))
			mapper.setMapping(act, userPropertyId)
			
		c(mapper, QtCore.SIGNAL("mapped(const int &)"), self.SLOT_setFormating)
		
		
	def setText(self,text=None,new_language=None,type='plain',
														local_dir=None):
		"""This method will set the text contained in text (when changing the 
		active scene for instance.
		- text : the text to insert (if None then it will insert u"")
		- new_language : the language of the text, if it is None, we keep the 
				previous one
		- type : 'plain' if raw text ; 'xml' if the personal format ; 'html' if 
				html
		- local_dir : local_dir of the file
		"""
		if text==None: text=""
		# We change the language if necessary
		if new_language!=None :
			if self.language.name!=new_language:
				self.changeLanguage(new_language)
		
		# Creating the new document with the good default format and inserting 
		# the text in it
		document=QtGui.QTextDocument(self)
		cursor , document= self.setDocumentFormat(document)
		
		self.local_dir = local_dir
		self.dict_autocorrection = CLAutoCorrection.get_values(
														local_dir=local_dir)
		if TEConstants['SPELL_CHECK'] and TEHasEnchant :
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
		if TEConstants["RECHECK_TEXT_OPEN"]:
			self.language.cheak_after_paste(cursor)
		
		self.blockSignals (True)
		self.setDocument(document)
		self.document().clearUndoRedoStacks() # It will empty the history (no 
															# "undo" before)
		self.blockSignals (False)

		self.setTextCursor(cursor)	
		
		
	
	################################# SLOTS ###################################
			
	def SLOT_cursorPositionChanged(self):
		"""Method that is called when the cursor position has just changed."""
		self.blockSignals (True) #allow the method to move the cursor in the 
									# method without calling itself one again.
									
		if self.old_cursor_position>=self.document().characterCount():
			# If we were at the end of the document and suppress the end, it 
			# does then nothing.
			self.old_cursor_position=self.textCursor().position()
			self.blockSignals (False)
			return self.old_cursor_position
		
		modification = False
		if TEConstants["AUTO_CORRECTION"]:
			# If we have just written a word (by a space, or a ponctuation) it 
			# makes the auto-correction of the word.
			cursor=self.textCursor()
			last_char=self.language.lastChar(cursor)
			list_word_break = [u' ',u'\u00A0',u'\n',u';',u':',u'!',u'?',u',',
					u'.',u"'",u'-']
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
				
		if TEConstants["DO_TYPOGRAPHY"]:
			# We check the typography at the site we just left
			cursor=QtGui.QTextCursor(self.document())
			cursor.clearSelection()
			cursor.setPosition(self.old_cursor_position)
			cursor.beginEditBlock()
			modification=self.language.correct_between_chars(cursor)
			cursor.endEditBlock()

		
		self.blockSignals (False)
		if modification:
			self.emit(QtCore.SIGNAL("typographyModification (PyQt_PyObject)"), 
					modification)
		self.old_cursor_position=self.textCursor().position() #update the 
															# cursor position
		return self.old_cursor_position
	
	def SLOT_textChanged(self):
		block_id = self.textCursor().blockFormat().property(
												QtGui.QTextFormat.UserProperty)
		block_id = block_id.toPyObject() 
		if block_id!=None and TSManager.dictStyle[block_id].protected :
			self.blockSignals (True)
			self.undo()
			self.blockSignals (False)
			self.emit(QtCore.SIGNAL("protectedStyleModification ( PyQt_PyObject)"), 
				"Try to modify a protected block (use Ctrl+L to delete it).")
		
	def SLOT_pluggins(self,iterator):
		"""Launch the pluggin corresponding to the iterator"""
		function=self.dico_pluggins[iterator]
		function(cursor=self.textCursor())
		
		
	def SLOT_actionLaunchCharWidgetTable(self):
		"""Slot that is called when we have to display the char table"""
		self.charWidgetTable.setVisible(True)
		
	def SLOT_actionLaunchFindDialog(self):
		"""Slot that is called when we have to display the search dialog 
		window."""
		self.findDialog.setVisible(True)

	def SLOT_actionFindNext	(self):
		"""Slot that is called when we have to display the next occurence of 
		the search dialog window"""
		self.findDialog.activate_next()
		
	def SLOT_actionFindPrevious	(self):
		"""Slot that is called when we have to display the previous occurence 
		of the search dialog window"""
		self.findDialog.activate_previous()
	
	def SLOT_actionRecheckTypography(self):
		"""Quick method that check and correct all the typography of the text.
		TODO : some summuary window of all the corrections.
		"""
		cursor=self.textCursor()
		cursor.setPosition(0)
		self.language.cheak_after_paste(cursor)
		
		
	def SLOT_actionChangeLanguage(self):
		"""Method that will display a QDialog that will enable to change the
		language. It will also propose to recheck all the typography with a 
		QCheckBox.		
		"""
		list_languages = TELanguageDico.keys() #list of the available languages
		assert self.language.name in list_languages , self.language.name + \
										" should be in te list of languages"
		
		# Create the dialog window
		dia = QtGui.QDialog (self)
		dia.setWindowTitle("New language")
		
		current_lge_index = list_languages.index(self.language.name)

		comboBox = QtGui.QComboBox()
		comboBox.addItems(TELanguageDico.keys())
		comboBox.setCurrentIndex(current_lge_index)
		
		checkBox = QtGui.QCheckBox("Re-check the typography")
		button_ok 		= QtGui.QPushButton('Ok')
		button_cancel 	= QtGui.QPushButton('Cancel')
		dia.connect(button_ok 		, QtCore.SIGNAL('clicked()'), dia.accept)
		dia.connect(button_cancel 	, QtCore.SIGNAL('clicked()'), dia.reject)
		
		layout=QtGui.QGridLayout()
		layout.addWidget(comboBox,0,0,1,1)
		layout.addWidget(checkBox,1,0,1,2)
		layout.addWidget(button_ok,2,0)
		layout.addWidget(button_cancel,2,1)
		
		dia.setLayout(layout)
		dia.exec_()
		
		# If the dialog is accepted, then it changes the language
		if dia.result () == QtGui.QDialog.Accepted:
			lang_name = list_languages [comboBox.currentIndex()]
			self.changeLanguage(language_name = unicode(lang_name))
			if checkBox.checkState () == QtCore.Qt.Checked:
				self.SLOT_actionRecheckTypography()

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
		
		# word = tuple_word_where[0]
		# if len(tuple_word_where)==1:
			# where='local'
		# else:
			# where = tuple_word_where[1]
		if self.parent().filepath==None:
			local_dir = None
		else:
			local_dir,tmp = os.path.split(self.parent().filepath)
		
		try :
			CLSpelling.add_words(words=[word],where=where,local_dir=local_dir)
			self.highlighter.dict.add(word)
			self.highlighter.rehighlight ()
			
		except IOError,e:
			QtGui.QMessageBox.critical(self,'Input error',e)
	
	def SLOT_setFormating(self,format_id):
		print 'format_id : ',format_id
		cursor=self.textCursor()
		cursor.beginEditBlock()
		self.blockSignals (True)
		TSManager.inverseStyle(cursor,format_id)
		cursor.endEditBlock()
		self.setTextCursor(cursor)
		self.blockSignals (False)
		QtCore.QObject.emit(self,QtCore.SIGNAL("somethingChanged ()"))
		# QtCore.QObject.emit(self,QtCore.SIGNAL("textChanged ()"))

	def SLOT_actionResetFormat(self):
		cursor=self.textCursor()
		cursor.beginEditBlock()
		self.blockSignals (True)
		TSManager.resetFormat(cursor)
		# self.setTextCursor(cursor)
		self.blockSignals (False)
		cursor.endEditBlock()
		QtCore.QObject.emit(self,QtCore.SIGNAL("somethingChanged ()"))
		
	def SLOT_actionInsertImage(self):
		if self.parent()!=None:
			dft_opening_site = self.parent().get_default_opening_saving_site()
			if self.parent().filepath!= None:
				local_dir,tmp = os.path.split(self.parent().filepath)
				local_dir = os.path.abspath(local_dir)
			else:
				local_dir = False
		else:
			dft_opening_site ='.'
			local_dir = False
		filepath = FMFileManagement.open_gui_filepath(
					dft_opening_site ,
					self,filter="Image Files (*.png *.jpg *.bmp *.gif)")
		
		if filepath:
			d,f = os.path.split(filepath)
			assert os.path.isabs(d) 
			
			if local_dir and d!=local_dir:
				assert os.path.isabs(local_dir)
				r = QtGui.QMessageBox.question(self, "Local importation", 
					"Do you want to import the file locally ?",
					QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
				if r== QtGui.QMessageBox.Yes:
					newfilepath = os.path.join(local_dir,f)
					newfilepath = FMFileManagement.exists(newfilepath)
					if not newfilepath:
						return False
					shutil.copyfile(filepath,newfilepath)
					tmp,newfilepath = os.path.split(newfilepath) #local path
			elif not local_dir:
				newfilepath = filepath
				r = QtGui.QMessageBox.question(self, "Local importation", 
					"Since you did not saved the file, the absolute path "+\
					"will be displayed. For import the file localy, save "+\
					"first",
					QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel)
				if r== QtGui.QMessageBox.Cancel:
					return False
			else :
				tmp,newfilepath = os.path.split(filepath)	#local path		
			
			# self.SLOT_setFormating(TSStyleImage.userPropertyId)
			self.blockSignals(True)
			
			cursor=self.textCursor()
			cursor.clearSelection()
			block_id = cursor.blockFormat().property(
												QtGui.QTextFormat.UserProperty)
			block_id = block_id.toPyObject() 
			if block_id==TSStyleImage.userPropertyId :
				# if there is an image, we remove the previous one
				TSManager.inverseStyle(cursor,block_id)
			TSManager.inverseStyle(cursor,TSStyleImage.userPropertyId)				
			cursor.beginEditBlock()
			cursor.insertText(newfilepath)
			cursor.endEditBlock()
			self.blockSignals(False)
			QtCore.QObject.emit(self,QtCore.SIGNAL("somethingChanged ()"))
			
			return filepath
		return False


	def insertFromMimeData(self,source ):
		"""A re-implementation of insertFromMimeData. We have to check the 
		typography of what we have just paste.
		TODO : some summary window of all the corrections.
		"""
		
		self.blockSignals (True)
		cursor=self.textCursor()
		cursor_pos=cursor.position()
		if source.html()==self.lastCopy[0].html():
			# if the pasted thing comes from the document itself
			cursor.insertFragment(self.lastCopy[1])
			size = self.lastCopy[1].toPlainText().size()
		else : 
			text=source.text()
			text.replace(QtCore.QString("\t"), QtCore.QString(" "))
			cursor.insertText(text)
			size = text.size()
			
		cursor.setPosition(cursor_pos)
		if TEConstants["DO_TYPOGRAPHY"]:
			self.language.cheak_after_paste(cursor,size) 
		self.blockSignals (False)
	
	
	def copy(self):
		"""A reimplementation of copy in order to remember what was the last 
		copy"""
		self.lastCopy = (self.createMimeDataFromSelection(),
						self.textCursor().selection() )
		QtGui.QTextEdit.copy(self)
		
	def cut(self):
		"""A reimplementation of cut in order to remember what was the last 
		copy"""
		self.lastCopy = (self.createMimeDataFromSelection(),
						self.textCursor().selection() )
		QtGui.QTextEdit.cut(self)
		
	def changeLanguage(self,language_name=None,local_dir=None):
		# fill self.language according to the language in entry
		if language_name==None:
			lang = TELanguageDico[TEConstants["DFT_WRITING_LANGUAGE"]]
			self.language=lang(self.dict_autocorrection)
		else :
			if not TELanguageDico.has_key(language_name):
				lang = TELanguageDico[TEConstants["DFT_WRITING_LANGUAGE"]]
				self.language=lang(self.dict_autocorrection)
				raise WWError("Do not have the typography for the language "+\
																language_name)
			else:
				lang = TELanguageDico[language_name]
				self.language = lang(self.dict_autocorrection)		
				
		## PROBLEM IF WE CHANGE OF LANGUAGE, WE KEEP THE OLD PLUGGINS		
		# add the language insert shortcuts to the class 
		dico = self.language.shortcuts_insert
		mapper = QtCore.QSignalMapper(self)
		for k in dico.keys():
			short=QtGui.QShortcut(QtGui.QKeySequence(*k),self)
			QtCore.QObject.connect(short,QtCore.SIGNAL("activated ()"), mapper,
														QtCore.SLOT("map()"))
			short.setContext(QtCore.Qt.WidgetShortcut)
			mapper.setMapping(short, dico[k])
		self.connect(mapper, QtCore.SIGNAL("mapped(const QString &)"), 
														self.insertPlainText )
		
		# add the language pluggins to the class 
		dico=self.language.shortcuts_correction_plugins
		self.dico_pluggins={}
		mapper = QtCore.QSignalMapper(self)
		for i,k in enumerate(dico.keys()):
			short=QtGui.QShortcut(QtGui.QKeySequence(*k),self)
			QtCore.QObject.connect(short,QtCore.SIGNAL("activated ()"), mapper,
														QtCore.SLOT("map()"))
			short.setContext(QtCore.Qt.WidgetShortcut)
			
			self.dico_pluggins[i]=dico[k]
			mapper.setMapping(short, i)		
		self.connect(mapper, QtCore.SIGNAL("mapped(int)"), self.SLOT_pluggins )
		
		# Change the Highlighter for the new language
		if TEConstants['SPELL_CHECK'] and TEHasEnchant :
			if local_dir!=None:
				list_spelling = CLSpelling.get_values(local_dir=local_dir)
			else:
				list_spelling=None
			self.highlighter = TEHighlighter(self.document(),self.language,
												list_spelling=list_spelling)
			self.highlighter.rehighlight ()
	
	def undo(self):
		"""
		This method do the usual undo, except in the case it has there has be a
		typography correction, in which case it comes back to the state before 
		the events that trigger the correction:
		exemple:
		"Hello,<space>you!"       
			-----     suppress coma     ----->       "Hello<space>you!"
			-----     another space     ----->       "Hello<space><space>you!"       
			----- typography correction ----->       "Hello<space>you!"
			-----        Ctrl-Z         ----->       "Hello,<space>you!"
		
		"""
		self.blockSignals (True)
		if TEConstants["DO_TYPOGRAPHY"]:
			i=1
			do_again=True
			while do_again and i<TEConstants["LIM_RECURSIV_UNDO"]:
				for j in range(i):
					QtGui.QTextEdit.undo(self)
				cursor=self.textCursor()
				cursor.clearSelection()
				do_again=self.language.correct_between_chars(cursor)
				i+=1
			self.blockSignals (False)
			self.old_cursor_position = self.textCursor().position() # update 
					# the cursor position
		else:
			QtGui.QTextEdit.undo(self)
	
		
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
		else:
			QtGui.QTextEdit.keyPressEvent(self,event)
	
	
		
	def toPlainText(self):
		"""
		Re-implementation of toplaintext in order to have the inbrekable spaces 
		(for a unkown reason it is not suported by the QTextEdit.toPlainText 
		function).
		"""
		cursor = QtGui.QTextCursor(self.document())
		cursor.select(QtGui.QTextCursor.Document)
		s = unicode(cursor.selectedText())
		s = s.replace(u'\u2029','\n')
		# res=u""
		# while not cursor.atEnd ():
			# cursor.movePosition(
					# QtGui.QTextCursor.Right,
					# QtGui.QTextCursor.KeepAnchor
					# )
			# if cursor.atBlockStart():
				# res+='\n'
			# else:
				# res+=unicode(cursor.selectedText())
			# cursor.clearSelection()
		return s
		
		
	def toXml(self):
		newText=self.toPlainText()
		newText=TSManager.toXml(newText,self.document())
		return newText
		
	def contextMenuEvent(self, event):
		cursor = QtGui.QTextCursor(self.document())
		cursor = self.cursorForPosition(event.pos())
		self.setTextCursor(cursor)		
		
		# popup_menu = self.createStandardContextMenu()
		popup_menu = QtGui.QMenu(self)
		
		
		if TEConstants['SPELL_CHECK'] and TEHasEnchant:
			# Select the word under the cursor.
			cursor = self.textCursor()
			cursor.select(QtGui.QTextCursor.WordUnderCursor)
			self.setTextCursor(cursor)

			# Check if the selected word is misspelled and offer spelling
			# suggestions if it is.
			if self.textCursor().hasSelection():
				text = unicode(self.textCursor().selectedText())
				text = self.highlighter.toRawWord(text)
				if not self.highlighter.dict.check(text):
					spell_menu = QtGui.QMenu('Spelling Suggestions')
					#for word in self.highlighter.dict.suggest(text):
					#	# action = SpellAction(word, spell_menu)
					#	action = QtGui.QAction(word, spell_menu)
					#	self.connect(action,QtCore.SIGNAL("triggered()"),
					#	action.triggered.connect(
					#		lambda x: action.correct.emit(word))
					#
					#	# action.correct.connect(self.correctWord)
					#	spell_menu.addAction(action)
						
					# Add wordcorrection to the mapper
					mapper = QtCore.QSignalMapper(self)
					for word in self.highlighter.dict.suggest(text):
						act = QtGui.QAction(word, spell_menu)
						
						QtCore.QObject.connect(
							act,
							QtCore.SIGNAL("triggered ()"), 
							mapper, 
							QtCore.SLOT("map()")
							)
						mapper.setMapping(act, word)
						spell_menu.addAction(act)
						
					self.connect(
						mapper, 
						QtCore.SIGNAL("mapped(const QString &)"), 
						self.SLOT_correctWord 
						)
					
					# Only add the spelling suggests to the menu if there are
					# suggestions.
					if len(spell_menu.actions()) != 0:
						spell_menu.addSeparator()
						act_loc = QtGui.QAction('Add word to local dict',
																	spell_menu)
						act_usr = QtGui.QAction('Add word to user dict',
																	spell_menu)
						act_glo = QtGui.QAction('Add word to global dict',
																	spell_menu)
						
						spell_menu.addAction(act_loc)
						spell_menu.addAction(act_usr)
						spell_menu.addAction(act_glo)
						
						if self.parent()==None or self.parent().filepath==None:
							act_loc.setEnabled(False)
						
						# Add word dictionary add to the mapper
						mapper = QtCore.QSignalMapper(self)
						c = QtCore.QObject.connect
						trig = QtCore.SIGNAL("triggered ()")
						
						slot_loc = lambda : self.SLOT_addWordSpelling(text,'local')
						slot_usr = lambda : self.SLOT_addWordSpelling(text,'user')
						slot_glo = lambda : self.SLOT_addWordSpelling(text,'global')
						
						c(act_loc,trig, slot_loc)
						c(act_usr,trig, slot_usr)
						c(act_glo,trig, slot_glo)
						
						# map = QtCore.SLOT("map()")
						# c(act_loc,trig, mapper, map)
						# mapper.setMapping(act, text,'local'))
						# c(act_usr,trig, mapper, map)
						# mapper.setMapping(act, text))
						# c(act_glo,trig, mapper, map)
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
		if TSConstants['DEFAULT_STYLE'].has_key("alignment"):
				
			align_name = TSConstants['DEFAULT_STYLE']["alignment"]
			if TSStyleClassBlock.dict_align.has_key(align_name):
				obt=QtGui.QTextOption(TSStyleClassBlock.dict_align[align_name])
				document.setDefaultTextOption(obt)
			else :
				KeyError('Unknown key for the alignement : '+align_name)
				
		font = document.defaultFont()
		if TSConstants['DEFAULT_STYLE'].has_key("font_name"):
			font.setFamily(TSConstants['DEFAULT_STYLE']["font_name"])
		if TSConstants['DEFAULT_STYLE'].has_key("font_size"):
			font.setPointSize(int(TSConstants['DEFAULT_STYLE']["font_size"]))
		document.setDefaultFont(font)
		
		cursor=QtGui.QTextCursor(document)
		format_block=cursor.blockFormat()
		
		# if TFConstants['DEFAULT_STYLE'].has_key("font_indent"):
			# format_block.setTextIndent(
								# TFConstants['DEFAULT_STYLE']["font_indent"])	
		if self.font_indent:
			format_block.setTextIndent (self.font_indent)
			
		if self.font_line_height:
			format_block.setLineHeight (self.font_line_height, 
									QtGui.QTextBlockFormat.ProportionalHeight)
			
		if self.doc_margin:
			document.setDocumentMargin(self.doc_margin)
			
		# Putting the cursor at the good format
		cursor.setBlockFormat(format_block)

		self.defaultBlockFormat = format_block
		self.defaultCharFormat = cursor.charFormat()
		self.defaultCharFormat.setFont(font)
		
		return cursor,document
					
	def emit_typographyModification(self):
		QtCore.QObject.emit(self,QtCore.SIGNAL("typographyModification ()"))
				

		
if __name__ == '__main__':

	import sys
	
	app = QtGui.QApplication(sys.argv)
	
	textedit = TETextEdit(language_name='French',parent=None)
	# button_refresh	 	= QtGui.QPushButton('Stupidity')
	# textedit.connect(textedit,QtCore.SIGNAL('typographyModification ()'), stupidity)
	# textedit.emit_typographyModification()
	# QtCore.QObject.connect(button_refresh,QtCore.SIGNAL('clicked ()'), textedit.toPlainText1)
	# textedit.typographyModification.connect(stupidity)
	textedit.show()
	# button_refresh.show()
	
	
	sys.exit(app.exec_())