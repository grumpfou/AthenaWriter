"""
Part of the AthenaWriterproject. Written by Renaud Dessalles.
It underline the words for spelling correction.
"""

TEHasEnchant = True

try :
	import enchant
except ImportError,e:
	print "Module Enchant not found !!!"
	TEHasEnchant = False
import re
import string


from PyQt4 import QtGui, QtCore
from TextLanguages.TextLanguages import TLEnchantDico
from TextEditPreferences import TEPreferences


class TEHighlighter (QtGui.QSyntaxHighlighter):
	# inspired by the code at http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
	
	WORDS = u'(?iu)[\w\'\u2019]+'	
	
	def __init__(self,parent,texteditlanguage,list_spelling=None):
		QtGui.QSyntaxHighlighter.__init__(self,parent)
		self.lang = TLEnchantDico[texteditlanguage.name]
		self.dict = enchant.Dict(self.lang)
		if list_spelling!=None:
			for w in list_spelling:
				self.dict.add(w)
	
	def highlightBlock(self, text):
		if TEPreferences['SPELL_CHECK'] :
			self.spellCheakHighlight(text)
		
	def getDefaultCharFormat(self,id=0):
		qtFormat = self.parent.defaultBlockFormat
		qtFormat.setProperty(QtGui.QTextFormat.UserProperty,id)
		return qtFormat
		
	def getDefaultBlockFormat(self,id=0):
		qtFormat = self.parent.defaultCharFormat
		qtFormat.setProperty(QtGui.QTextFormat.UserProperty,id)
		return qtFormat
	
	def spellCheakHighlight(self,text):
		if not self.dict :
			return None

		text = unicode(text)

		format = QtGui.QTextCharFormat()
		format.setUnderlineColor(QtCore.Qt.red)
		format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)

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
		return string.replace(word,u'\u2019',u"'")
	
class TESpellingAddWordDialog (QtGui.QDialog):	
	def __init__(self,metadata=None,dft_opening_saving_site=None,
				default_path='./Untitled.txt',*args,**kargs):
		"""A dialog that will permit to add a word to the disctionnary"""
		self.combo_dict = QtGui.QComboBox ()
		self.lineedit_mainword = QtGui.QLineEdit ()
		self.lineedit_flexions = QtGui.QLineEdit ()
		button_generate = QtGui.QPushButton("&Generate")
		button_export = QtGui.QPushButton("&Add")
		button_cancel = QtGui.QPushButton("&Cancel")		
		
		
		self.main_layout=QtGui.QFormLayout()
		self.main_layout.addRow(u'Dictionary'	,self.combo_dict)
		self.main_layout.addRow(u'Main word'	,self.lineedit_mainword)
		self.main_layout.addRow(u'Other forms'	,button_generate)
		self.main_layout.addRow(self.lineedit_flexions)
		
		layout_button =  QtGui.QHBoxLayout()
		layout_button.addWidget( button_add )
		layout_button.addWidget( button_cancel )		
		
		self.main_layout.addRow(layout_button)
		self.setLayout ( self.main_layout )
		
				
		
	
	
	@staticmethod
	def getFields(*args,**kargs):
		
		dialog = TESpellingAddWordDialog(*args,**kargs)
		result = dialog.exec_()
		
		if result == QtGui.QDialog.Accepted:

			# def f (r):
				# r = unicode(r)
				# if r=="" : return None
				# return r
			d ={}
			d['format_name']	= unicode(dialog.combo_format.currentText())
			d['filepath']		= unicode(dialog.lineedit_path.text())
			d['check_typo']		= (dialog.check_typo.checkState() == \
															QtCore.Qt.Checked)
			dd = dialog.widget_options.getValueDict()
			d = dict(d.items()+dd.items())
			return d	
		else:
			return False	
	
if __name__ == '__main__':
	from TextEdit import *
	
	
	app = QtGui.QApplication(sys.argv)
	
	textedit = TETextEdit(language_name='French',parent=None)
	textedit.highlighter = TEHighlighter(textedit.document(),textedit.language)
	textedit.show()
	
	
	import sys
	sys.exit(app.exec_())
