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
from TextEditLanguages import *


class TEHighlighter (QtGui.QSyntaxHighlighter):
	# inspired by the code at http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
	
	WORDS = u'(?iu)[\w\'\u2019]+'	
	
	def __init__(self,parent,texteditlanguage):
		QtGui.QSyntaxHighlighter.__init__(self,parent)
		self.lang = TELanguageEnchantDico[texteditlanguage.name]
		self.dict = enchant.Dict(self.lang)
	
	def highlightBlock(self, text):
		if TEConstants['SPELL_CHECK'] :
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
	
	
	
if __name__ == '__main__':
	from TextEdit import *
	
	
	app = QtGui.QApplication(sys.argv)
	
	textedit = TETextEdit(language_name='French',parent=None)
	textedit.highlighter = TEHighlighter(textedit.document(),textedit.language)
	textedit.show()
	
	
	import sys
	sys.exit(app.exec_())