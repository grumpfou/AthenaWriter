
class TLRuleFrench0001 (TLRuleAbstract):
	number = 1
	title="No space before a space or a break of line"
	description=	\
		"It deletes the space before another space of a break of line\n"+\
		"example :	'A  thing' -> 'A thing' \n"+\
		"			'end of block. \\n' -> 'end of block.\\n'"
	profile = 0
	in_languges=[u'French']

	def correct(self,last_char,next_char,cursor):
		if last_char==u' ' and next_char in [u' ',u'\n']:
			cursor.deletePreviousChar()
			return True
		return False

class TLRuleFrench0002 (TLRuleAbstract):
	number = 2
	title="No space or non-breakable space after an non-breakable space"
	description=	\
		"It delete the space or an non-breakable space [⎵] after an "+\
		"non-breakable space. \n"+\
		"example :	'year⎵ 2001' -> 'year⎵2001' \n"+\
		"			'year⎵⎵2001' -> 'year⎵2001'"
	profile = 0
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u00A0' and next_char in [u'\u00A0',' ']:
			cursor.deleteChar()
			return True
		return False

class TLRuleFrench0003 (TLRuleAbstract):
	number = 3
	title="No space or non-breakable space  after a break of line."

	description=	\
		"It deletes the space after a break of line\n"+\
		"example :	'end of block.\\n ' -> 'end of block.\\n'\n"+\
		"example :	'end of block.\\n⎵' -> 'end of block.\\n'\n"
	in_languges=[u'French']
	profile = 0
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\n' and next_char in [u' ',u'\u00A0']:
			cursor.deleteChar()
			return True
		return False
class TLRuleFrench0003_old (TLRuleAbstract):
	title="No space, non-breakable space or break of line after a break of line."

	description=	\
		"It deletes the space or break of line after a break of line\n"+\
		"example :	'end of block.\\n ' -> 'end of block.\\n'\n"+\
		"example :	'end of block.\\n⎵' -> 'end of block.\\n'\n"+\
		"			'end of block.\\n\\n' -> 'end of block.\\n'"
	in_languges=[u'French']
	profile = 0
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\n' and next_char in [u' ',u'\n',u'\u00A0']:
			cursor.deleteChar()
			return True
		return False
class TLRuleFrench0004 (TLRuleAbstract):
	number = 4
	title="An non-breakable space before [;], [:], [!], [?], and closing "+\
		"guillemets."
	description=	\
		"Put an non-breakable space [⎵] before some ponctuation : [;], [:], "+\
		"[!], [?] and the french closing guillemets.\n"+\
		"example :	'Bonjour! ' -> 'Bonjour⎵!'\n"+\
		"			'Bonjour; ' -> 'Bonjour⎵;'\n"+\
		"			'Bonjour: ' -> 'Bonjour⎵:'\n"+\
		"			'Bonjour? ' -> 'Bonjour⎵?'\n"+\
		"			'Bonjour ! ' -> 'Bonjour⎵!'\n"+\
		"			'Bonjour ? ' -> 'Bonjour⎵?'"
	profile = 1
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if next_char in [u';',u':',u'!',u'?',u'\u00BB']:
			if last_char==' ':
				cursor.deletePreviousChar()
				cursor.insertText(u'\u00A0')
				return True
			if last_char!=u'\u00A0':
				cursor.insertText(u'\u00A0')
				return True
		return False

class TLRuleFrench0005 (TLRuleAbstract):
	number = 5
	title="An non-breakable space after an opening guillemet"
	description=	\
		"It puts an non-breakable space [⎵] after an opening gullemet [«] "+\
		"(or replace the simple space that was there).\n"+\
		"example :	'« Bonjour' -> '«⎵Bonjour'\n"+\
		"			'«Bonjour' -> '«⎵Bonjour'"
	profile = 1
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u00AB':
			if next_char==' ':
				cursor.deleteChar()
				cursor.insertText(u'\u00A0')
				return True
			if next_char!=u'\u00A0':
				cursor.insertText(u'\u00A0')
				return True
		return False

class TLRuleFrench0006 (TLRuleAbstract):
	number = 6
	title="No non-breakable space if it is not before a ponctuation or after "+\
			"an oppening guillemet or after a dialog dash, or a number."
	description=	\
		"Usually we prevent using an non-breakable space [⎵] if it is not "+\
		"before a ponctuation like [;], [:], [!], [?], or a closing "+\
		"guillemet or a dialog dash [–] or a number. It can also be used after "+\
		"an opening guillemet. It replaces the non-breakable space by a "+\
		"simple space.\n"+\
		"example :	'Je⎵suis' -> 'Je suis'\n"+\
		"			'«⎵Bonjour' -> '«⎵Bonjour' (same)\n"+\
		"			'Bonjour⎵!' -> 'Bonjour⎵!' (same)\n"+\
		"			'–⎵Salut' -> '–⎵Salut' (same)\n"+\
		"			'200⎵000' -> '200⎵000' (same)"
	profile = 1
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u00A0' and (next_char not in \
											[u';',u':',u'!',u'?',u'\u00BB']+\
											[str(i) for i in range(10)]):
			last_last_char=self.language.lastChar(cursor,n=2)
			# we cheak it caused by an oppening "guillemet":
			if last_last_char not in [u'\u00AB' , u'\u2014']:
				cursor.deletePreviousChar()
				cursor.insertText(u' ')
				return True
		return False

class TLRuleFrench0007 (TLRuleAbstract):
	number = 7
	title="No space before a point or a comma."
	description=	\
		"It deletes a space or an non-breakable space [⎵] before a comma.\n"+\
		"example :	'Très bien .' -> 'Très bien.'\n"+\
		"			'Très bien⎵.' -> 'Très bien.'\n"+\
		"			'Charles , toi et moi.' -> 'Charles, toi et moi.'\n"
	profile = 0
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char in [u' ', u'\u00A0'] and next_char in [u'.',u',']:
			cursor.deletePreviousChar()
			return True
		return False

class TLRuleFrench0008 (TLRuleAbstract):
	number = 8
	title="A space or a newline after [;] or [:]."
	description=	\
		"Check if there is a newline or a space after [;] or [:] and if it "+\
		"is not the case, it inserts one (replacing the non-breakable space "+\
		"is necessary.\n"+\
		"example :	'Oui;et vous' -> 'Oui; et vous'\n"+\
		"			'Oui:cela est cohérent' -> 'Oui: cela est cohérent'\n"+\
		"			'Je lui dis:\\n' -> 'Je lui dis:\\n' (same) \n"
	profile = 0
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char in [u';',u':'] and (next_char not in [u'\n',u' ']):
			if next_char== u'\u00A0':
				cursor.deleteChar()
			cursor.insertText(u' ')
			return True

		return False

class TLRuleFrench0009 (TLRuleAbstract):
	number = 9
	title="Replace the typewriter apostrophe by a curved apostrophe."
	description=	\
		"Replace a the char ['] by a curved apostrophe [’].\n\
		example :	'C'est moi' -> 'C’est moi'"
	profile = 1
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if next_char==u"'":
			cursor.deleteChar()
			cursor.insertText(u'\u2019')
			return True
		return False

class TLRuleFrench0010 (TLRuleAbstract):
	number = 10
	title="Replace the char [\"] by a opening or closing guillemet"
	description=	\
		"When pressing the char [\"], it replace by : an opening guillemet "+\
		"[«] if it is preceded by a space, an non-breakable space [⎵] or a "+\
		"newline ; a closing guillemet [»] otherwise. It also insert an "+\
		"non-breakable space after the opening guillemet and before the "+\
		"closing guillemet.\n"+\
		"example :	'\"Bonjour' -> '«⎵Bonjour'"+\
		"			'Salut.\"' -> 'Salut.⎵»'"
	profile = 1
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if next_char==u'"':
			if last_char in [u' ',u'\n',u'\u00A0']:
				cursor.deleteChar()
				cursor.insertText(u'\u00AB\u00A0')
			else :
				cursor.deleteChar()
				cursor.insertText(u'\u00A0\u00BB')
			return True

		return False


class TLRuleFrench0011 (TLRuleAbstract):
	number = 11
	title="Replace 3 consecutive points by an ellipsis."
	description=	\
		"Replace 3 consecutive points into an ellipsis […]:\n"+\
		"example :	'\"So...' -> 'So…'"
	profile = 1
	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char==u'.' and next_char==u'.':

			if self.language.lastChar(cursor,n=2)==u'.':
				cursor.deleteChar()
				cursor.deletePreviousChar()
				cursor.deletePreviousChar()
				cursor.insertText(u'\u2026')
				return True
		return False

class TLRuleFrench0012 (TLRuleAbstract):
	number = 12
	title="An non-breakable space before after a diolog dash."
	description=	\
		"It puts an non-breakable space [⎵] after a diolog dash [—] (or "+\
		"replace the simple space that was there).\n\
		example :	'— Bonjour' -> '—⎵Bonjour'\n\
					'—Bonjour' -> '—⎵Bonjour"
	profile = 1

	in_languges=[u'French']
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u2014' and next_char!=u'\u00A0':
			if next_char==' ':
				cursor.deleteChar()
				cursor.insertText(u'\u00A0')
				return True
			if next_char!=u'\u00A0':
				cursor.insertText(u'\u00A0')
				return True
		return False

class TLWordCorrectionRuleFrench13 (TLRuleAbstract):
	number = 13
	title=u"Replace the [oe] by [œ] and [OE] or [Oe] by [Œ]"
	description=	\
		"In French, most of the word with 'oe' have an elision"
	profile = 1
	in_languges=[u'French']

	def correct(self,last_word,cursor):
		if last_word.find(u'oe')!=-1:
			if last_word not in {'moelle'}:
				return last_word.replace(u'oe',u'\u0153')
		elif last_word.find(u'Oe')!=-1:
				return last_word.replace(u'Oe',u'Œ')
		elif last_word.find(u'OE')!=-1:
				return last_word.replace(u'OE',u'Œ')

		return False


def plugin_dialogCorrection(language,cursor):
	for block in cursor.yieldBlockInSelection():
		cur_tmp=QtGui.QTextCursor(block)
		next_char=language.nextChar(cur_tmp)
		if next_char=='\u2014':
			cur_tmp.deleteChar()
		else:
			cur_tmp.insertText('\u2014')
		language.correct_between_chars(cur_tmp)



language = Language(
	name="French",
	code="fr",
	code_enchant="fr_FR",
	afterCharRules=[	TLRuleFrench0001,
						TLRuleFrench0002,
						TLRuleFrench0003,
						TLRuleFrench0004,
						TLRuleFrench0005,
						TLRuleFrench0006,
						TLRuleFrench0007,
						TLRuleFrench0008,
						TLRuleFrench0009,
						TLRuleFrench0010,
						TLRuleFrench0011,
						TLRuleFrench0012],
	afterWordRules = [ TLWordCorrectionRuleFrench13 ],
	shortcuts_insert={
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_A)	:"\u00C0",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_Comma	,QtCore.Qt.SHIFT+QtCore.Qt.Key_C)	:"\u00C7",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_4		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:"\u00C9",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:"\u00C8"}
			,
	shortcuts_correction_plugins={
		(QtCore.Qt.CTRL+QtCore.Qt.Key_D,)	: plugin_dialogCorrection ,
		# (QtCore.Qt.CTRL+QtCore.Qt.Key_L,)	: self.delete_bloc       ,
		},
	delimiters = {
				'«':(u'«\u00A0',u'\u00A0»'),
				'"':(u'«\u00A0',u'\u00A0»'),
				'(':('(',')'),
				'[':('[',']'),
				}
		)
