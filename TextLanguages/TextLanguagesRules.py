
from PyQt5 import QtGui, QtCore, QtWidgets
from CommonObjects.CommonObjects import COChoice,COTextCursorFunctions
from .TextLanguages import TLLanguage
from TextEdit.TextEditPreferences import TEDictCharReplace


all_quotes = ("“„«「","”»」")
all_spaces = ' \u00A0'

class TLRuleAbstract:
	title="None"
	description="None"
	dictCharReplace = TEDictCharReplace
	def __init__(self,language):
		self.language=language
		self.createTitleDescription()
		pass

	def __str__(self):
		return self.title+'\n'+self.description

	def correct(self,last_char,next_char,cursor):
		raise NotImplementedError
		return False

	def createTitleDescription(self): pass # To reimplement if needed


class TLRuleCommon0001 (TLRuleAbstract):
	title="No space before a space or a break of line"
	description=	\
		"It deletes the space before another space of a break of line\n"+\
		"example :	'A  thing' → 'A thing' \n"+\
		"			'end of block. \\n' → 'end of block.\\n'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if last_char==u' ' and next_char in [u' ',u'\n']:
			cursor.deletePreviousChar()
			return True
		return False

class TLRuleCommon0002 (TLRuleAbstract):
	title="No space or non-breakable space after an non-breakable space"
	description=	\
		"It delete the space or an non-breakable space [⎵] after an "+\
		"non-breakable space. \n"+\
		"example :	'year⎵ 2001' → 'year⎵2001' \n"+\
		"			'year⎵⎵2001' → 'year⎵2001'"
	profile = 0
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u00A0' and next_char in [u'\u00A0',' ']:
			cursor.deleteChar()
			return True
		return False

class TLRuleCommon0003 (TLRuleAbstract):
	title="No space or non-breakable space  after a break of line."

	description=	\
		"It deletes the space after a break of line\n"+\
		"example :	'end of block.\\n ' → 'end of block.\\n'\n"+\
		"example :	'end of block.\\n⎵' → 'end of block.\\n'\n"
	profile = 0
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\n' and next_char in [u' ',u'\u00A0']:
			cursor.deleteChar()
			return True
		return False

class TLRuleCommon0004 (TLRuleAbstract):
	title="No  break of line after a break of line."

	description=	\
		"It deletes the space or break of line after a break of line\n"+\
		"			'end of block.\\n\\n' → 'end of block.\\n'"
	profile = 0
	def correct(self,last_char,next_char,cursor):
		if (not cursor.atEnd()) and last_char==u'\n' and next_char == '\n':
			cursor.deleteChar()
			return True
		return False


class TLRuleCommon0005 (TLRuleAbstract):

	def createTitleDescription(self):
		self.title="Replace the char [\"] by a opening [%s] or closing quotation mark [%s]"%(self.language.quotes[0],self.language.quotes[1])
		self.description=	\
			"When pressing the key [\"], it replace by : an opening quatation mark "+\
			"[“] if it is preceded by a space, an non-breakable space [⎵] or a "+\
			"newline ; a closing quatation mark [%s] otherwise. It also insert an "%self.language.quotes[1]+\
			"non-breakable space after the opening quatation mark and before the "+\
			"closing quatation mark.\n"+\
			"example :	'\"Hello' → '%sHello'\n"%self.language.quotes[0]+\
			"			'Bye.\"' → 'Bye.%s'"%self.language.quotes[1]

	profile = 1
	def correct(self,last_char,next_char,cursor):
		if next_char==u'"':
			if last_char in [u' ',u'\n',u'\u00A0']:
				cursor.deleteChar()
				COTextCursorFunctions.insertText(cursor,self.language.quotes[0])
			else :
				cursor.deleteChar()
				COTextCursorFunctions.insertText(cursor,self.language.quotes[1])
			return True

		return False

class TLRuleCommon0006 (TLRuleAbstract):
	profile = 1

	def createTitleDescription(self):
		self.diff_quotes = ([s for s in all_quotes[0] if s!=self.language.quotes[0]] ,
		[s for s in all_quotes[1] if s!=self.language.quotes[1]])
		op_ex = all_quotes[0][0] if all_quotes[0][0]!=self.language.quotes[0] else all_quotes[0][1]
		cl_ex = all_quotes[1][0] if all_quotes[1][0]!=self.language.quotes[1] else all_quotes[1][1]
		self.title = "Replace the foreign quotes (like [%s,%s]) "%(op_ex,cl_ex)+\
					"by the language quotes [%s,%s]"%self.language.quotes
		diff_quotes = (''.join([s for s in all_quotes[0] if s!=self.language.quotes[0]]) ,
		 			   ''.join([s for s in all_quotes[1] if s!=self.language.quotes[1]]))
		self.description = \
			"Replaces the quote from other languages (%s) and (%s) "%diff_quotes+\
			"by their own quotes [%s] and [%s].\n"%self.language.quotes+\
			"example : '%sHello!' → '%sHello'"%(op_ex,self.language.quotes[0])+\
			"          'Bye%s' → 'Bye%s'"%(cl_ex,self.language.quotes[1])

	def correct(self,last_char,next_char,cursor):
		if last_char in self.diff_quotes[0]:
			cursor.deletePreviousChar()
			COTextCursorFunctions.insertText(cursor,self.language.quotes[0])
			return True
		elif last_char in self.diff_quotes[1]:
			cursor.deletePreviousChar()
			COTextCursorFunctions.insertText(cursor,self.language.quotes[1])
			return True
		return False


class TLRuleCommon0007(TLRuleAbstract):
	profile = 1
	def createTitleDescription(self):
		if self.language.inside_quotes is None:
			self.title = "Remove all space after an opening quote or before a closing quote."
			self.description =\
				"If a space or unbreakable space [⎵] is found before a closing "+\
				"quote, it removes it.\n"+\
				"example : '%s⎵Hello!' →  '%sHello!'\n"%(self.language.quotes[0],self.language.quotes[0])+\
				"          ' Bye…⎵%s' →  'Bye…%s'"%(self.language.quotes[1],self.language.quotes[1])
		else:
			self.title = "Add the char [%s] after an opening quote and after a closing quote"%self.dictCharReplace.get(self.language.inside_quotes)
			self.description = \
				"If an opening quote is not followed by [%s] "%self.dictCharReplace.get(self.language.inside_quotes)+\
				"or a closing quote is not preceeded by [%s] "%self.dictCharReplace.get(self.language.inside_quotes)+\
				"it adds it."+\
				"example : '%sBonjour,' → '%s%sHello'"%(self.language.quotes[0],self.language.inside_quotes,self.language.quotes[0])+\
				"          'Au revoir%s,' → 'Au revoir%s%s'"%(self.language.quotes[0],self.language.inside_quotes,self.language.quotes[0])


	def correct(self,last_char,next_char,cursor):
		if self.language.inside_quotes==None:
			if last_char==self.language.quotes[0] and next_char in all_spaces:
				cursor.deleteChar()
				return True
			elif last_char in all_spaces  and next_char==self.language.quotes[1]:
				cursor.deletePreviousChar()
				return True
		else:
			if last_char==self.language.quotes[0] and next_char!=self.language.inside_quotes:
				COTextCursorFunctions.insertText(cursor,self.language.inside_quotes)
				return True
			elif last_char!=self.language.inside_quotes  and next_char==self.language.quotes[1]:
				COTextCursorFunctions.insertText(cursor,self.language.inside_quotes)
				return True

		return False

class TLRuleCommon0008 (TLRuleAbstract):
	profile = 0
	def createTitleDescription(self):
		self.title="A space, non-breakable space or a newline after [.,;:] except if it is a "+\
			"figure or a closing quoation mark [%s] or another dot"%self.language.quotes[1]
		self.description=	\
			"Check if there is a newline or a space after [.] or [,] and if it "+\
			"is not the case, it inserts one (replacing the non-breakable space "+\
			"is necessary. This rule does not apply if the next character is a "+\
			"figure.\n"+\
			"example :	'I agree.And you' → 'I agree. And you'\n"+\
			"			'I agree,it is coherent' → 'I agree, it is coherent'\n"+\
			"			'I agree.%s' → 'I agree.%s' (same)\n"%(self.language.quotes[1],self.language.quotes[1])+\
			"			'The speed was 33.7 mph' → 'The speed was 33.7 mph' (same)\n"+\
			"			'It is 10:30 PM' → 'It is 10:30 PM' (same)\n"+\
			"			'Let's see..' →  'Let's see..' (same, the goal is to make an ellips)"

	def correct(self,last_char,next_char,cursor):
		ch_list = [u'\n',u' ',u'\u00A0',self.language.quotes[1],u'.']+[str(i) for i in range(10)]
		if last_char in '.,;:' and (next_char not in ch_list):
			COTextCursorFunctions.insertText(cursor,u' ')
			return True

		return False


class TLRuleCommon0009 (TLRuleAbstract):
	profile = 0
	def createTitleDescription(self):
		self.title="A space or a newline after punctuations [!?], except "+\
			"if it is a closing quoation mark [%s] or another  punctuations [!?]."%self.language.quotes[1]
		self.description=	\
			"Check if there is a newline or a space after [;!?]."+\
			"example :	'I agree!And you' → 'I agree! And you'\n"+\
			"			'I agree;it is coherent' → 'I agree; it is coherent'\n"+\
			"			'I agree.%s' → 'I agree.%s' (same)\n"%(self.language.quotes[1],self.language.quotes[1])+\
			"			'What?!' → 'What?!' (same)\n"

	def correct(self,last_char,next_char,cursor):
		ch_list = [u'\n',u' ',u'\u00A0',self.language.quotes[1],'!','?']
		if last_char in'!?' and (next_char not in ch_list):
			COTextCursorFunctions.insertText(cursor,u' ')
			return True

		return False


class TLRuleCommon0010 (TLRuleAbstract):

	title="Replace the typewriter apostrophe by a curved apostrophe."
	description=	\
		"Replace a the char ['] by a curved apostrophe [’].\n\
		example :	'It's me' → 'It’s me'"

	profile = 1
	def correct(self,last_char,next_char,cursor):
		if next_char==u"'":
			cursor.deleteChar()
			COTextCursorFunctions.insertText(cursor,u'\u2019')
			return True
		return False

class TLRuleCommon0011 (TLRuleAbstract):
	title="Replace 3 consecutive points by an ellipsis."
	description=	\
		"Replace 3 consecutive points into an ellipsis […]:\n\
		example :	'\"So...' → 'So…'"
	profile = 1

	def correct(self,last_char,next_char,cursor):
		if last_char==u'.' and next_char==u'.':

			if self.language.lastChar(cursor,n=2)==u'.':
				cursor.deleteChar()
				cursor.deletePreviousChar()
				cursor.deletePreviousChar()
				COTextCursorFunctions.insertText(cursor,u'\u2026')
				return True
		return False


## We upload all the dictionaries in ./languages/
class TLDicoClass (dict):
	def __getitem__(self,key):
		if key==None:
			# if key==None, returns the default one
			return dict.__getitem__(self,TLPreferences['DFT_WRITING_LANGUAGE'])
		if key not in self:
			warnings.warn(("Unknown language specified `%s`,"
											" take English instead")%key)
			assert "English" in self, "I can not even get the english dictionary!"
			return self["English"]
		else:
			return dict.__getitem__(self,key)

TLDico = TLDicoClass()

import pathlib
f = pathlib.Path(__file__).absolute().parent
f /= "./languages/"
Language = TLLanguage # for compatibility with RTypography
for lang_file in f.glob('*.py'):
	with lang_file.open() as ff:
		exec(ff.read())
		TLDico[language.name] = language

TLChoice = COChoice(sorted(TLDico.keys()))
