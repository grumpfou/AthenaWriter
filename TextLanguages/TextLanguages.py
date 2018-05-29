"""
Part of the  project AthenaWriter. Written by Renaud Dessalles
Contains the class that deal with the typograpgy.
The TLLanguage class is the model class of all the language class
below. Instance of this class will represent a language. They are defined in the
./languages directory.

There is two ways of correcting the typography of the user :
- by checking during the editing : every time the cursor moves (a char is
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
from TextEdit.TextEditPreferences import TEHasEnchant, TEDictCharReplace,TEPreferences
from TextStyles.TextStyles import TSManager
from CommonObjects.CommonObjectsWord import *
from CommonObjects.CommonObjects import COChoice,COTextCursorFunctions
if TEHasEnchant:
	import enchant
import warnings





def plugin_deleteBloc(language,cursor):
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


class TLLanguage:

	#The pluggins common to all languages:
	shortcuts_correction_plugins = {(QtCore.Qt.CTRL+QtCore.Qt.Key_L,):plugin_deleteBloc}

	def __init__(self,name,code,code_enchant,
				afterCharRules=[],afterWordRules=[],shortcuts_insert={},
				shortcuts_correction_plugins={},dict_autocorrection={},
				profile=None,delimiters=[],quotes=None,inside_quotes=None):
		"""
		name: name of the Language (e.g.: "English" or "French")
		code: code of the language (e.g.: "en" for English, "fr" for French)
		afterCharRules : list of TLRuleAbstract subclass that need to be check
			after each char.
		afterWordRules : list of TLRuleAbstract subclass that need to be check
			after each words.
		shortcuts_insert : dict to insert chars specific to the language under
			the form of {KeySequence:char_to_insert}
		shortcuts_correction_plugins : dict to pluggins specific to the language
			under the form of {KeySequence:function_to_execute} where
			function_to_execute takes into argument the QTextCursor.
		delimiters : list of 2-elements tuples (or dictionaries), that
			represents the different delimiters of the language (like
			parentheses, quotations marks, etc.).
		quotes : List of two elements like ["«","»"] representing the opening
			and closing quote marks of the language
		inside_quotes : The character (ususally non-breakable space) that should
			be after an openning quote and before a closing quote.
		"""
		# for rule in afterCharRules : assert issubclass(rule,TLRuleAbstract)
		# for rule in afterWordRules : assert issubclass(rule,TLRuleAbstract)
		self.name = name
		self.code = code
		self.code_enchant = code_enchant
		assert not (quotes is None)

		self.quotes =  quotes
		self.inside_quotes = inside_quotes

		self.shortcuts_insert = shortcuts_insert
		self.shortcuts_correction_plugins .update( shortcuts_correction_plugins)
		self.dictCharReplace = TEDictCharReplace
		self.update(dict_autocorrection=dict_autocorrection,profile=profile)
		self.delimiters = dict(delimiters)
		self.afterCharRules = [rule(language=self) for rule in afterCharRules]
		self.afterWordRules = [rule(language=self) for rule in afterWordRules]

	def update(self,dict_autocorrection=False,profile=False):
		if dict_autocorrection!=False:
			self.dict_autocorrection = COWordDico(dict_autocorrection)
		if profile!=False:
			self.profile = TLPreferences['DFT_TYPO_PROFILE'] if (profile is None) else profile


	def correct_between_chars(self,cursor):
		"""Function that will be called everytime the cursor moves. It
		check the respect of all the typography rules of the two char of
		both sides of the position that the cursor has just left."""

		block_id = cursor.blockFormat().property(
											QtGui.QTextFormat.UserProperty)
		# # block_id = block_id.toPyObject()
		if block_id!=None and TSManager.dictStyle[block_id].protected :
			return False

		last_char = COTextCursorFunctions.lastChar(cursor)
		next_char = COTextCursorFunctions.nextChar(cursor)

		for rule in self.afterCharRules:
			if self.profile <= rule.profile:
				res=rule.correct(last_char,next_char,cursor)
				if res :
					return (rule,cursor.position())


		return False

	def insert_delimiters(self,delim_key,cursor):
		assert delim_key in self.delimiters
		if cursor.hasSelection():
			selectionStart	= cursor.selectionStart()
			selectionEnd	= cursor.selectionEnd()
			position		= cursor.position()

			l1 = len(self.delimiters[delim_key][0])
			l2 = len(self.delimiters[delim_key][1])

			cursor.beginEditBlock()
			cursor.setPosition(selectionStart)
			COTextCursorFunctions.insertText(cursor,self.delimiters[delim_key][0])
			cursor.setPosition(selectionEnd+l1)
			COTextCursorFunctions.insertText(cursor,self.delimiters[delim_key][1])
			cursor.setPosition(selectionStart+l1,QtGui.QTextCursor.MoveAnchor)
			cursor.setPosition(selectionEnd+l1,QtGui.QTextCursor.KeepAnchor)
			cursor.endEditBlock()
			# cursor.setPosition(position+l1,QtGui.QTextCursor.KeepAnchor)

		else:
			cursor.beginEditBlock()
			COTextCursorFunctions.insertText(cursor,self.delimiters[delim_key][0])
			COTextCursorFunctions.insertText(cursor,self.delimiters[delim_key][1])
			cursor.movePosition(QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor,len(self.delimiters[delim_key][1]))
			cursor.endEditBlock()

		return cursor


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
			text = cur_tmp.selectedText ()
			for k,v in self.dictCharReplace.items():
				text = text.replace(v,k)
			return text

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
			text = cur_tmp.selectedText ()
			for k,v in self.dictCharReplace.items():
				text = text.replace(v,k)
			return text

	def correct_between_chars_recurs(self,cursor):
		"""
		Will check the typography at the position until no modification is made
		or until the LIM_RECURSIV_TYPO is reached.
		"""
		i = 0
		modified = False
		res = True
		res_list = []
		while res and i<TEPreferences["LIM_RECURSIV_TYPO"]:
			res = self.correct_between_chars(cursor)
			res_list.append(res)
			if res: modified=res
			i = i+1

		if i == TEPreferences["LIM_RECURSIV_TYPO"]:
			print("LIM_RECURSIV_TYPO reached at posistion %i."%(cursor.position()))
		return modified
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



	def check_after_paste(self,cursor,nb_ite=-1):
		"""Method that will be called after a paste. It will correct the
		typography from the position of the cursor during nb_ite. If nb_ite is
		-1 then it will do the correction until the end of the document."""
		i=0
		res=False
		res_tmp=self.correct_between_chars_recurs(cursor)
		res=res or res_tmp
		while cursor.movePosition(QtGui.QTextCursor.Right) and i!=nb_ite:
			res_tmp=self.correct_between_chars_recurs(cursor)
			res=res or res_tmp
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
				COTextCursorFunctions.insertText(cur_tmp,word)
			return replace
		return False







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
	for k,v in list(TLDico.items()):
		if v.code_enchant in enchant.list_languages():
			d = enchant.Dict(v.code_enchant)
			i = 0
			for w in a:
				if d.check(w):
					i += 1
			if i>i_max:
				i_max = i
				k_max = k
	return k_max


from .TextLanguagesRules import *



# TLDico = {"French":TLFrench,"English":TLEnglish}
# TLEnchantDico={"French":'fr_FR',"English":'en_UK'}


if __name__ == '__main__':
	pass
# Language=LanguageEnglish()
