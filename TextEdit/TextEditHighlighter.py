"""
Part of the AthenaWriterproject. Written by Renaud Dessalles.
It underline the words for spelling correction.
"""
import re




from PyQt5 import QtGui, QtCore, QtWidgets
from TextLanguages.TextLanguages import TLEnchantDico
from .TextEditPreferences import TEPreferences,TEHasEnchant
if TEHasEnchant :
	import enchant

class TEHighlighter (QtGui.QSyntaxHighlighter):
	# inspired by the code at http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/

	WORDS = '(?iu)[\w\'\u2019]+'

	def __init__(self,parent,texteditlanguage,list_spelling=None):
		QtGui.QSyntaxHighlighter.__init__(self,parent)
		self.lang = TLEnchantDico[texteditlanguage.name]
		self.dict = enchant.Dict(self.lang)
		if list_spelling!=None:
			for w in list_spelling:
				self.dict.add(w)

	def highlightBlock(self, text):
		if TEPreferences['SPELL_CHECK'] :
			self.spellCheckHighlight(text)

	def getDefaultCharFormat(self,id=0):
		qtFormat = self.parent.defaultBlockFormat
		qtFormat.setProperty(QtGui.QTextFormat.UserProperty,id)
		return qtFormat

	def getDefaultBlockFormat(self,id=0):
		qtFormat = self.parent.defaultCharFormat
		qtFormat.setProperty(QtGui.QTextFormat.UserProperty,id)
		return qtFormat


	def spellCheckHighlight(self,text):
		if not self.dict :
			return None

		text = str(text)

		format = QtGui.QTextCharFormat()
		format.setUnderlineColor(QtCore.Qt.red)
		format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)

		for word_object in re.finditer(self.WORDS, text):
			word = word_object.group()
			word = self.toRawWord(word)
			if not self.dict.check(word):
				self.setFormat(word_object.start(),
					word_object.end() - word_object.start(), format)



	def toRawWord(self,word):
		"""This function is needed to change the word of AthW to a word
		understandable by enchant. Indeed, the enchant module do not recognize
		the curve apostrophe"""
		return word.replace('\u2019',"'")

class TESpellingAddWordDialog (QtWidgets.QDialog):
	def __init__(self,metadata=None,dft_opening_saving_site=None,
				default_path='./Untitled.txt',*args,**kargs):
		"""A dialog that will permit to add a word to the disctionnary"""
		self.combo_dict = QtWidgets.QComboBox ()
		self.lineedit_mainword = QtWidgets.QLineEdit ()
		self.lineedit_flexions = QtWidgets.QLineEdit ()
		button_generate = QtWidgets.QPushButton("&Generate")
		button_export = QtWidgets.QPushButton("&Add")
		button_cancel = QtWidgets.QPushButton("&Cancel")


		self.main_layout=QtWidgets.QFormLayout()
		self.main_layout.addRow('Dictionary'	,self.combo_dict)
		self.main_layout.addRow('Main word'	,self.lineedit_mainword)
		self.main_layout.addRow('Other forms'	,button_generate)
		self.main_layout.addRow(self.lineedit_flexions)

		layout_button =  QtWidgets.QHBoxLayout()
		layout_button.addWidget( button_add )
		layout_button.addWidget( button_cancel )

		self.main_layout.addRow(layout_button)
		self.setLayout ( self.main_layout )





	@staticmethod
	def getFields(*args,**kargs):

		dialog = TESpellingAddWordDialog(*args,**kargs)
		result = dialog.exec_()

		if result == QtWidgets.QDialog.Accepted:

			# def f (r):
				# r = unicode(r)
				# if r=="" : return None
				# return r
			d ={}
			d['format_name']	= str(dialog.combo_format.currentText())
			d['filepath']		= str(dialog.lineedit_path.text())
			d['check_typo']		= (dialog.check_typo.checkState() == \
															QtCore.Qt.Checked)
			dd = dialog.widget_options.getValueDict()
			d = dict(list(d.items())+list(dd.items()))
			return d
		else:
			return False

if __name__ == '__main__':
	from .TextEdit import *


	app = QtWidgets.QApplication(sys.argv)

	textedit = TETextEdit(language_name='French',parent=None)
	textedit.highlighter = TEHighlighter(textedit.document(),textedit.language)
	textedit.show()


	import sys
	sys.exit(app.exec_())
