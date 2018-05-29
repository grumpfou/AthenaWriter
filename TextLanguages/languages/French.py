class TLRuleFrench0001 (TLRuleAbstract):
	profile = 1
	def createTitleDescription(self):
		self.title="An non-breakable space before [;], [:], [!], [?], and closing "+\
			"guillemets."
		self.description=	\
			"Put an non-breakable space [⎵] before some ponctuation : [;], [:], "+\
			"[!], [?] or [%s]. The exepctions are numbers before [;:] "%self.language.quotes[1]+\
			"and puntucations [!?] after [!?].\n"+\
			"example :	'Bonjour! ' → 'Bonjour⎵!'\n"+\
			"			'Bonjour; ' → 'Bonjour⎵;'\n"+\
			"			'Bonjour: ' → 'Bonjour⎵:'\n"+\
			"			'Bonjour? ' → 'Bonjour⎵?'\n"+\
			"			'Bonjour ! ' → 'Bonjour⎵!'\n"+\
			"			'Bonjour ? ' → 'Bonjour⎵?'\n"+\
			"			'10:30' → '10:30' (same)\n"+\
			"			'10;30' → '10;30' (same)\n"+\
			"			'Pardon⎵?!' → 'Pardon⎵?!' (same)\n"

	def correct(self,last_char,next_char,cursor):
		if next_char in (';:!?'+self.language.quotes[1]):
			if  next_char in ';:' and last_char in [str(i) for i in range(10)]:
				return False
			if  next_char in '?!' and last_char in '?!':
				return False
			if last_char==' ':
				cursor.deletePreviousChar()
				COTextCursorFunctions.insertText(cursor,u'\u00A0')
				return True
			if last_char!=u'\u00A0':
				COTextCursorFunctions.insertText(cursor,u'\u00A0')
				return True
		return False

class TLRuleFrench0002 (TLRuleAbstract):
	title="No non-breakable space if it is not before a ponctuation or after "+\
			"an oppening guillemet or after a dialog dash, or a number."
	description=	\
		"Usually we prevent using an non-breakable space [⎵] if it is not "+\
		"before a ponctuation like [;], [:], [!], [?], or a closing "+\
		"guillemet or a dialog dash [–] or a number. It can also be used after "+\
		"an opening guillemet. It replaces the non-breakable space by a "+\
		"simple space.\n"+\
		"example :	'Je⎵suis' → 'Je suis'\n"+\
		"			'«⎵Bonjour' → '«⎵Bonjour' (same)\n"+\
		"			'Bonjour⎵!' → 'Bonjour⎵!' (same)\n"+\
		"			'–⎵Salut' → '–⎵Salut' (same)\n"+\
		"			'200⎵000' → '200⎵000' (same)"
	profile = 1
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u00A0' and (next_char not in \
											[u';',u':',u'!',u'?',u'\u00BB']+\
											[str(i) for i in range(10)]):
			last_last_char=self.language.lastChar(cursor,n=2)
			# we check it caused by an oppening "guillemet":
			if last_last_char not in [u'\u00AB' , u'\u2014']:
				cursor.deletePreviousChar()
				COTextCursorFunctions.insertText(cursor,u' ')
				return True
		return False

class TLRuleFrench0003 (TLRuleAbstract):
	title="No space before a point or a comma."
	description=	\
		"It deletes a space or an non-breakable space [⎵] before a comma.\n"+\
		"example :	'Très bien .' → 'Très bien.'\n"+\
		"			'Très bien⎵.' → 'Très bien.'\n"+\
		"			'Charles , toi et moi.' → 'Charles, toi et moi.'\n"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if last_char in [u' ', u'\u00A0'] and next_char in [u'.',u',']:
			cursor.deletePreviousChar()
			return True
		return False


# class TLRuleFrench0007 (TLRuleCommonQuote0001):
# 	quotes = ("\u00AB\u00A0","\u00A0\u00BB")
# 	title="Replace the char [\"] by a opening or closing guillemet"
# 	description=	\
# 		"When pressing the char [\"], it replace by : an opening guillemet "+\
# 		"[«] if it is preceded by a space, an non-breakable space [⎵] or a "+\
# 		"newline ; a closing guillemet [»] otherwise. It also insert an "+\
# 		"non-breakable space after the opening guillemet and before the "+\
# 		"closing guillemet.\n"+\
# 		"example :	'\"Bonjour' → '«⎵Bonjour'"+\
# 		"			'Salut.\"' → 'Salut.⎵»'"


class TLRuleFrench0004 (TLRuleAbstract):
	title="An non-breakable space before after a diolog dash."
	description=	\
		"It puts an non-breakable space [⎵] after a diolog dash [—] (or "+\
		"replace the simple space that was there).\n\
		example :	'— Bonjour' → '—⎵Bonjour'\n\
					'—Bonjour' → '—⎵Bonjour"
	profile = 1

	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u2014' and next_char!=u'\u00A0':
			if next_char==' ':
				cursor.deleteChar()
				COTextCursorFunctions.insertText(cursor,u'\u00A0')
				return True
			if next_char!=u'\u00A0':
				COTextCursorFunctions.insertText(cursor,u'\u00A0')
				return True
		return False

class TLWordCorrectionRuleFrench001 (TLRuleAbstract):
	title=u"Replace the [oe] by [œ] and [OE] or [Oe] by [Œ]"
	description=	\
		"In French, most of the word with 'oe' have an elision"
	profile = 1


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
	for block,_ in COTextCursorFunctions.yieldBlock(cursor):
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
	afterCharRules=[
						TLRuleCommon0001,
						TLRuleCommon0002,
						TLRuleCommon0003,
						TLRuleCommon0004,
						TLRuleCommon0005,
						TLRuleCommon0006,
						TLRuleCommon0007,
						TLRuleCommon0008,
						TLRuleCommon0009,
						TLRuleCommon0010,
						TLRuleCommon0011,
						TLRuleFrench0001,
						TLRuleFrench0002,
						TLRuleFrench0003,
						TLRuleFrench0004,
						],
	afterWordRules = [ TLWordCorrectionRuleFrench001 ],
	shortcuts_insert={
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_A)	:"\u00C0",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_Comma	,QtCore.Qt.SHIFT+QtCore.Qt.Key_C)	:"\u00C7",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_4		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:"\u00C9",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_7		,QtCore.Qt.SHIFT+QtCore.Qt.Key_E)	:"\u00C8",
			(QtCore.Qt.CTRL+QtCore.Qt.Key_Space	,)									:"\u00A0"}
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
				},
	quotes = ("«","»"),
	inside_quotes = "\u00A0",

		)
