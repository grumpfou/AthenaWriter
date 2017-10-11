"""
Part of the  project AthenaWriter. Written by Renaud Dessalles
Contains the class that deal with the typograpgy.
The TLAbstract class is the model class of all the language class
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
from PyQt5 import QtGui, QtCore, QtWidgets

from .TextLanguagesPreferences import *
from .TextLanguagesRules import *
from TextEdit.TextEditPreferences import TEHasEnchant, TEDictCharReplace
from TextStyles.TextStyles import TSManager
from CommonObjects.CommonObjectsWord import *
from CommonObjects.CommonObjects import COChoice

import enchant

class TLAbstract:
	name=''
	encoding=''
	shortcuts_insert={}
	def __init__(self,dict_autocorrection=None,profile=None):
		"""
		- profile: int; the number above which we consider teh rule
		"""
		### We are creating the autocorrection:
		if dict_autocorrection==None: dict_autocorrection={}

		self.dict_autocorrection=COWordDico(dict_autocorrection)
		self.shortcuts_correction={	}
		self.rules=[]
		if profile == None:
			profile = TLPreferences['DFT_TYPO_PROFILE']
		self.profile = profile
		self.dictCharReplace = TEDictCharReplace



	def correct_between_chars(self,cursor):
		"""Function that will be called everytime the cursor moves. It
		check the respect of all the typography rules of the two char of
		both sides of the position that the cursor has just left."""

		block_id = cursor.blockFormat().property(
											QtGui.QTextFormat.UserProperty)
		# # block_id = block_id.toPyObject()
		if block_id!=None and TSManager.dictStyle[block_id].protected :
			return False

		last_char=self.lastChar(cursor)
		next_char=self.nextChar(cursor)

		for rule in self.afterCharRules:
			if self.profile <= rule.profile:
				res=rule.correct(last_char,next_char,cursor)
				if res :
					return (rule,cursor.position())


		return False

	def lastChar(self,cursor,n=1):
		"""Return the left char at the distance n from the cursor (n=1 means
		the one just on the left)."""
		if cursor.atBlockStart():
			return '\n'
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
		"""Return the right char at the distance n from the cursor (n=1 means
		the one just on the right)."""
		if cursor.atBlockEnd():
			return '\n'
		else :
			cur_tmp=QtGui.QTextCursor(cursor)
			cur_tmp.clearSelection()
			for i in range(n-1):
				cur_tmp.movePosition(QtGui.QTextCursor.Right,
												QtGui.QTextCursor.MoveAnchor)
				if cur_tmp.atBlockEnd():
					return '\n'
			cur_tmp.movePosition (QtGui.QTextCursor.Right,
											QtGui.QTextCursor.KeepAnchor,n=n)
			return cur_tmp.selectedText ()

	def getWordUnderCursor(self,cursor,char_exception=None):
		"""
		Return the word under the cursor. char_exception in entry should be
		the list of the chars that should not be considered as word break (
		usfull to take  words like "I'am" or "re-invented").
		"""
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
		"""Method that will be called after a paste. It will correct the
		typography from the position of the cursor during nb_ite. If nb_ite is
		-1 then it will do the correction until the end of the document."""
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
		"""Function which is called after a word has just been witten. It
		replaces some things that are specific to the language. It also correct
		the word if there has some auto-correction to make."""
		cur_tmp=QtGui.QTextCursor(cursor)
		cur_tmp.clearSelection()

		block_id = cur_tmp.blockFormat().property(
											QtGui.QTextFormat.UserProperty)
		# # block_id = block_id.toPyObject()
		if block_id!=None and TSManager.dictStyle[block_id].protected :
			return False

		if cur_tmp.movePosition (QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor,1):
			word,cur_tmp=self.getWordUnderCursor(cur_tmp)
			replace=False

			# We replace things due to the language : 'oe' as a elision for
			# instance
			word_replace=str(word)
			id = COWordTools.whatID(word_replace)
			word_replace=word_replace.lower()
			for rule in self.afterWordRules:
				word_replace=rule.correct(word_replace,cursor)
				if word_replace :
					word = COWordTools.toID(word_replace,id)
					replace=True

			# We replace things due to the language user settings.
			# Example: 'gvt' --> 'government'
			word_replace=self.dict_autocorrection.get(word,False)
			if word_replace:
				word=word_replace
				replace=True

			if replace:
				cur_tmp.insertText(word)
			return replace
		return False





class TLEnglish (TLAbstract):
	encoding='utf-8'
	name='English'
	shortcuts_insert={}


	def __init__(self,*args,**kargs):
		TLAbstract.__init__(self,*args,**kargs)
		self.shortcuts_correction_plugins={}
		self.afterCharRules=[	\
						TLRuleEnglish0001(language=self),
						TLRuleEnglish0002(language=self),
						TLRuleEnglish0003(language=self),
						TLRuleEnglish0004(language=self),
						TLRuleEnglish0005(language=self),
						TLRuleEnglish0006(language=self),
						TLRuleEnglish0007(language=self),
						TLRuleEnglish0008(language=self),
						TLRuleEnglish0009(language=self),
						TLRuleEnglish0010(language=self),
						TLRuleEnglish0011(language=self)]
		self.afterWordRules = [	]

	def wordCorrection(self,word):
		return False




class TLFrench (TLAbstract):
	encoding='utf-8'
	name='French'
	shortcuts_insert={
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_A)	:"\u00C0",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_Comma	,QtCore.Qt.SHIFT+QtCore.Qt.Key_C)	:"\u00C7",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_4		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:"\u00C9",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:"\u00C8"}


	def __init__(self,*args,**kargs):
		TLAbstract.__init__(self,*args,**kargs)
		self.shortcuts_correction_plugins={
			(QtCore.Qt.CTRL+QtCore.Qt.Key_D,)	: self.dialog_correction ,
			(QtCore.Qt.CTRL+QtCore.Qt.Key_L,)	: self.delete_bloc       ,
			}
		self.afterCharRules=[	TLRuleFrench0001(language=self),
						TLRuleFrench0002(language=self),
						TLRuleFrench0003(language=self),
						TLRuleFrench0004(language=self),
						TLRuleFrench0005(language=self),
						TLRuleFrench0006(language=self),
						TLRuleFrench0007(language=self),
						TLRuleFrench0008(language=self),
						TLRuleFrench0009(language=self),
						TLRuleFrench0010(language=self),
						TLRuleFrench0011(language=self),
						TLRuleFrench0012(language=self),
						TLRuleFrench0013(language=self)]

		self.afterWordRules = [
			TLWordCorrectionRuleFrench0001(language=self),
			]


	def dialog_correction(self,cursor):
		for block in cursor.yieldBlockInSelection():
			cur_tmp=QtGui.QTextCursor(block)
			next_char=self.nextChar(cur_tmp)
			if next_char=='\u2014':
				cur_tmp.deleteChar()
			else:
				cur_tmp.insertText('\u2014')
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
		cur_tmp.setPosition(endCursor.position(), QtGui.QTextCursor.KeepAnchor)
		cur_tmp.deleteChar()

TLDico = {"French":TLFrench,"English":TLEnglish}
TLEnchantDico={"French":'fr_FR',"English":'en_UK'}


def TLGuessLanguages(text):
	if not TEHasEnchant:
		return TLDico[TLPreferences['DFT_WRITING_LANGUAGE']]

	a =  str(text[:min(len(text),TLPreferences['GUESS_NB_CHAR'])])
	a = [a]
	splitter = "\n .,;!?"
	for c in splitter:
		a_tmp = [w.split(c) for w in a]
		a = [w1 for w2 in a_tmp for w1 in w2]
		a = [w for w in a if len(w)>0]

	k_max = TLPreferences['DFT_WRITING_LANGUAGE']
	i_max = 0
	for k,v in list(TLEnchantDico.items()):
		d = enchant.Dict(v)
		i = 0
		for w in a:
			if d.check(w):
				i += 1
		print("v,i : ",v,i)
		if i>i_max:
			i_max = i
			k_max = k
	return k_max




class TLChoice(COChoice):			# bofff
	elements_list = list(TLDico.keys())	# bofff



if __name__ == '__main__':
	pass
# Language=LanguageEnglish()
