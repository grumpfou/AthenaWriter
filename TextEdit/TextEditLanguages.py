"""
Part of the  project AthenaWriter. Written by Renaud Dessalles
Contains the class that deal with the typograpgy.
The TELanguageAbstract class is the model class of all the language class 
below. It must not be used directly, only subclass should be used.

There is two ways of correcting the typography of the user :
- by cheaking during the editing : every time the cursor moves (a char is 
inserted or a the user moves the cursor), the software is cheking if the chars 
around the place leaved by the cursor are correct, and correct them if 
necessary. The method used to do so is correct_between_chars.
- after a word is written : to correct the previous word etc. The method used 
to do so is wordCorrection.
The class can also contain some pluggin usefull in the language :
- the shortcuts_insert dict allow to insert specific text after a shortcut
- the shortcuts_correction_plugins dict allow to do a more complex modification 
of the text.

When creating a new Language class, it must contain :
- the encoding
- the name of the language (in the language)
- possibly the shortcuts_insert (a dictionary where the key is a tuple 
containing the sequence of the shortcut and the value is the string to insert.
_ a __init__ method with :
	a dictionary shortcuts_correction_plugins dict : 
		key : shortcuts_correction_plugins 
		value : the name of the pluggin method
	self.rules : the list of the rules (contained in the file 
		WolfWriterLanguagesRules.py) that will be check by the 
		correct_between_chars method. Note that the order of the list is the 
		same in which the rule will be checked.
- a possibly reimplementation of the wordCorrection method
- the possibly method mentioned in the values of the 
	shortcuts_correction_plugins
"""
from PyQt4 import QtGui, QtCore

from TextEditLanguagesRules import *
from TextEditConstants import *
from TextEditWord import *




class TELanguageAbstract:
	name=u''
	encoding=''
	shortcuts_insert={}
	def __init__(self,dict_autocorrection=None):
		### We are creating the autocorrection:
		if dict_autocorrection==None: dict_autocorrection={}
			
		self.dict_autocorrection=TEWordDico(data_dict=dict_autocorrection)
		self.shortcuts_correction={	}
		self.rules=[]
		
	
	def correct_between_chars(self,cursor):
		# Function that will be called everytime the cursor moves. It check the 
		# respect of all the typography rules of the two char of both sides of 
		# the position that the cursor has just left.

		last_char=self.lastChar(cursor)
		next_char=self.nextChar(cursor)
		
		
		for rule in self.rules:
			res=rule.correct(last_char,next_char,cursor)
			if res :
				return (rule,cursor.position())
			
		return False
		
	def lastChar(self,cursor,n=1):
		# Return the left char at the distance n from the cursor (n=1 means 
		# the one just on the left).
		if cursor.atBlockStart():
			return u'\n'		
		else :
			cur_tmp=QtGui.QTextCursor(cursor)
			cur_tmp.clearSelection()
			for i in range(n-1):
				cur_tmp.movePosition(QtGui.QTextCursor.Left,
												QtGui.QTextCursor.MoveAnchor)
				if cur_tmp.atBlockStart():
					return '\n'		
			cur_tmp.movePosition (QtGui.QTextCursor.Left,
												QtGui.QTextCursor.KeepAnchor)
			return cur_tmp.selectedText ()

	def nextChar(self,cursor,n=1):
		# Return the right char at the distance n from the cursor (n=1 means 
		# the one just on the right).		
		if cursor.atBlockEnd():
			return u'\n'		
		else :
			cur_tmp=QtGui.QTextCursor(cursor)
			cur_tmp.clearSelection()
			for i in range(n-1):
				cur_tmp.movePosition(QtGui.QTextCursor.Right,
												QtGui.QTextCursor.MoveAnchor)
				if cur_tmp.atBlockEnd():
					return u'\n'				
			cur_tmp.movePosition (QtGui.QTextCursor.Right,
											QtGui.QTextCursor.KeepAnchor,n=n)
			return cur_tmp.selectedText ()
			
	def getWordUnderCursor(self,cursor,char_exception=None):
		# Return the word under the cursor. char_exception in entry should be 
		# the list of the chars that should not be considered as word break 
		# (usfull to take  words like "I'am" or "re-invented").
		if char_exception==None : char_exception=[]
		cur_start=QtGui.QTextCursor(cursor)
		cur_start.clearSelection()
		cur_end=QtGui.QTextCursor(cursor)
		cur_end.clearSelection()
		
		regexp=QtCore.QRegExp("\\b")
		
		cur_start=cur_start.document().find(regexp,cur_start,
											QtGui.QTextDocument.FindBackward)
		while self.lastChar( cur_start ) in char_exception:
			cur_start.movePosition(QtGui.QTextCursor.Left,
												QtGui.QTextCursor.MoveAnchor)
			cur_start=cur_start.document().find(regexp,cur_start,
											QtGui.QTextDocument.FindBackward)
		cur_end=cur_end.document().find(regexp,cur_end)
		while self.nextChar( cur_end ) in char_exception:
			cur_end.movePosition(QtGui.QTextCursor.Right,
											QtGui.QTextCursor.MoveAnchor,n=2)
			cur_end=cur_end.document().find(regexp,cur_end)
		
		n=cur_end.position()-cur_start.position()
		cur_start.movePosition(QtGui.QTextCursor.Right,
											QtGui.QTextCursor.KeepAnchor,n=n)
		return cur_start.selectedText(),cur_start
		

	def cheak_after_paste(self,cursor,nb_ite=-1):
		# Method that will be called after a paste. It will correct the typography from
		# the position of the cursor during nb_ite. If nb_ite is -1 then it will do the
		# correction until the end of the document.
		i=0
		res=False
		res_tmp=self.correct_between_chars(cursor)
		res=res or res_tmp		
		while cursor.movePosition(QtGui.QTextCursor.Right) and i!=nb_ite:
			res_tmp=self.correct_between_chars(cursor)
			res=res or res_tmp
			i+=1
		return res
	
	def afterWordWritten(self,cursor):
		# Function which is called after a word has just been witten. It replaces some
		# things that are specific to the language. It also correct the word if there
		# has some auto-correction to make.
		cur_tmp=QtGui.QTextCursor(cursor)
		cur_tmp.clearSelection()
		if cur_tmp.movePosition (QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor,1):
			word,cur_tmp=self.getWordUnderCursor(cur_tmp)
			replace=False
			
			#We replace things due to the language : 'oe' as a elision for instance
			word_replace=self.wordCorrection(word)
			if word_replace:
				word=word_replace
				replace=True
				
			#We replace things due to the language user settings : 'gvt' --> 'government'
			word_replace=self.dict_autocorrection.get(word)
			if word_replace:
				word=word_replace
				replace=True
				
			if replace:
				cur_tmp.insertText(word)
			return replace
		return False

	def wordCorrection(self):
		# To reimplement if the language has some specific correction to make. For
		# instance, in French, it is correct to make elisions of the two chars 'oe' 
		# into a single char.
		raise False
		
	

	
class TELanguageEnglish (TELanguageAbstract):
	encoding='utf-8'
	name=u'English'
	shortcuts_insert={}
	
	
	def __init__(self,*args,**kargs):
		TELanguageAbstract.__init__(self,*args,**kargs)
		self.shortcuts_correction_plugins={}
		self.rules=[	\
						TERuleEnglish0001(language=self),
						TERuleEnglish0002(language=self),
						TERuleEnglish0003(language=self),
						TERuleEnglish0004(language=self),
						TERuleEnglish0005(language=self),
						TERuleEnglish0006(language=self),
						TERuleEnglish0007(language=self),
						TERuleEnglish0008(language=self),
						TERuleEnglish0009(language=self),
						TERuleEnglish0010(language=self),
						TERuleEnglish0011(language=self)]
						
	
	def wordCorrection(self,word):
		return False


			
	
class TELanguageFrench (TELanguageAbstract):
	encoding='utf-8'
	name=u'French'
	shortcuts_insert={
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_A)	:u"\u00C0",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_Comma	,QtCore.Qt.SHIFT+QtCore.Qt.Key_C)	:u"\u00C7",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_4		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:u"\u00C9",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:u"\u00C8"}
	
	
	def __init__(self,*args,**kargs):
		TELanguageAbstract.__init__(self,*args,**kargs)
		self.shortcuts_correction_plugins={
			(QtCore.Qt.CTRL+QtCore.Qt.Key_D,)	: self.dialog_correction ,
			(QtCore.Qt.CTRL+QtCore.Qt.Key_L,)	: self.delete_bloc       ,
			}
		self.rules=[	TERuleFrench0001(language=self),
						TERuleFrench0002(language=self),
						TERuleFrench0003(language=self),
						TERuleFrench0004(language=self),
						TERuleFrench0005(language=self),
						TERuleFrench0006(language=self),
						TERuleFrench0007(language=self),
						TERuleFrench0008(language=self),
						TERuleFrench0009(language=self),
						TERuleFrench0010(language=self),
						TERuleFrench0011(language=self),
						TERuleFrench0012(language=self),
						TERuleFrench0013(language=self)]

	def wordCorrection(self,word):
		word=unicode(word)
		id=TEWordTools.whatID(word)
		word=word.lower()
		if word=='--':
			return u"\u2014"
		if word.find(u'oe')!=-1:
			word=word.replace(u'oe',u'\u0153')
			word=TEWordTools.toID(word,id)
			word=TEWordTools.toID(word,id)
			return word
		
		else:
			return False

	def dialog_correction(self,cursor):
		for block in cursor.yieldBlockInSelection():
			cur_tmp=QtGui.QTextCursor(block)
			next_char=self.nextChar(cur_tmp)
			if next_char==u'\u2014':
				cur_tmp.deleteChar()
			else:
				cur_tmp.insertText(u'\u2014')
			self.correct_between_chars(cur_tmp)

	def delete_bloc(self,cursor):
		pos1=cursor.selectionStart()
		pos2=cursor.selectionEnd ()
		startCursor=QtGui.QTextCursor(cursor)
		endCursor=QtGui.QTextCursor(cursor)
		startCursor.setPosition(pos1)
		endCursor  .setPosition(pos2)
		startCursor. movePosition(QtGui.QTextCursor.StartOfBlock)
		endCursor  . movePosition(QtGui.QTextCursor.EndOfBlock)

		cur_tmp=QtGui.QTextCursor(startCursor)
		cur_tmp.setPosition(endCursor.position(), QtGui.QTextCursor.KeepAnchor);
		cur_tmp.deleteChar()
	
TELanguageDico={"French":TELanguageFrench,"English":TELanguageEnglish}			
TELanguageEnchantDico={"French":'fr_FR',"English":'en_UK'}			


	
# Language=LanguageEnglish()