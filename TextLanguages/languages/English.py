

class TLRuleEnglish0001 (TLRuleAbstract):
	number = 1
	title="No space before a space or a break of line"
	description=	\
		"It deletes the space before another space of a break of line\n \n\
		example :	'A  thing' -> 'A thing' \n\
					'end of block. \\n' -> 'end of block.\\n'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if last_char==u' ' and next_char in [u' ',u'\n']:
			cursor.deletePreviousChar()
			return True
		return False

class TLRuleEnglish0002 (TLRuleAbstract):
	number = 2
	title="No space or non-breakable space after an non-breakable space"
	description=	\
		"It delete the space or an non-breakable space [⎵] after an "+\
		"non-breakable space. \n"+\
		"example :	'year⎵ 2001' -> 'year⎵2001' \n"+\
		"			'year⎵⎵2001' -> 'year⎵2001'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u00A0' and next_char in [u'\u00A0',' ']:
			cursor.deleteChar()
			return True
		return False

class TLRuleEnglish0003 (TLRuleAbstract):
	number = 3
	title="No space or non-breakable space  after a break of line."

	description=	\
		"It deletes the space after a break of line\n"+\
		"example :	'end of block.\\n ' -> 'end of block.\\n'\n"+\
		"example :	'end of block.\\n⎵' -> 'end of block.\\n'\n"
	profile = 0
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\n' and next_char in [u' ',u'\u00A0']:
			cursor.deleteChar()
			return True
		return False
class TLRuleEnglish0003old (TLRuleAbstract):
	title="No space or break of line after a break of line. "

	description=	\
		"It deletes the space or break of line after a break of line\n"+\
		"example :	'end of block.\\n ' -> 'end of block.\\n'\n"+\
		"				'end of block.\\n\\n' -> 'end of block.\\n'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if last_char==u'\n' and next_char in [u' ',u'\n']:
			cursor.deleteChar()
			return True
		return False

class TLRuleEnglish0004 (TLRuleAbstract):
	number = 4
	title="No space or non-breakable space before [,], [;], [:], [!], [?]"
	description=	\
		"Delete a space or an non-breakable space [⎵] before some "+\
		"ponctuation: [;], [:], [!], [?] or a closing quotation mark [”].\n"+\
		"example :	'Hello !' 		-> 'Hello!'\n"+\
		"			'Hello⎵!'		-> 'Hello!'\n"+\
		"			'Hello ;'	 	-> 'Hello;'\n"+\
		"			'Hello⎵;' 		-> 'Hello;'\n"+\
		"			'Hello :'		-> 'Hello:'\n"+\
		"			'Hello ?'		-> 'Hello?'\n"+\
		"			'Hello. ”'	-> 'Hello.”'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if next_char in [u',',u';',u':',u'!',u'?',u'\201d']:
			if last_char==' ' or last_char==u'\u00A0':
				cursor.deletePreviousChar()
				return True
		return False


class TLRuleEnglish0005 (TLRuleAbstract):
	number = 5
	title="Replace the char [\"] by a opening [“] or closing quatation mark [”]"
	description=	\
		"When pressing the char [\"], it replace by : an opening quatation mark "+\
		"[“] if it is preceded by a space, an non-breakable space [] or a "+\
		"newline ; a closing quatation mark [”] otherwise. It also insert an "+\
		"non-breakable space after the opening quatation mark and before the "+\
		"closing quatation mark.\n"+\
		"example :	'\"Hello' -> '“Hello'\n"+\
		"			'Bye.\"' -> 'Bye.”'"

	profile = 1
	def correct(self,last_char,next_char,cursor):
		if next_char==u'"':
			if last_char in [u' ',u'\n',u'\u00A0']:
				cursor.deleteChar()
				cursor.insertText(u'\u201c')
			else :
				cursor.deleteChar()
				cursor.insertText(u'\u201d')
			return True

		return False

class TLRuleEnglish0006 (TLRuleAbstract):
	number = 6
	title="No space or non-breakable space after an opening guillemet."
	description=	\
		"It deletes any space or non-breakable space [⎵] after an opening "+\
		"quatation mark [“].\n"+\
		"example :	'“ Hello' -> '“Hello'\n"+\
		"			'“⎵Hello' -> '“Hello'"

	profile = 1
	def correct(self,last_char,next_char,cursor):
		if last_char==u'\u201c':
			if next_char==' ' or next_char==u'\u00AB':
				cursor.deleteChar()
				return True
		return False

class TLRuleEnglish0007 (TLRuleAbstract):
	number = 7
	title="No space or non-breakable space before an closing guillemet."
	description=	\
		"It deletes any space or non-breakable space [⎵] before an closing "+\
		"quatation mark ”.\n"+\
		"example :	'Hello ”' 	-> 'Hello”'\n"+\
		"			'Hello⎵”' -> 'Hello”'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if next_char==u'\u201d':
			if last_char==' ' or last_char==u'\u00AB':
				cursor.deletePreviousChar()
				return True
		return False



class TLRuleEnglish0008 (TLRuleAbstract):
	number = 8
	title="A space or a newline after [;], [:], [!] or [?] except if it is a "+\
		"closing quotation mark [”] or [!], [?]"
	description=	\
		"Check if there is a newline or a space after [;], [:], [!] or [?] "+\
		"and if it is not the case, it inserts one (replacing the "+\
		"non-breakable space is necessary).\n"+\
		"example :	'I agree;and you' -> 'I agree; and you'\n"+\
		"			'I agree:it is coherent' -> 'I agree: it is coherent'\n"+\
		"			'I agree!It is coherent' -> 'I agree! It is coherent'\n"+\
		"			'Do you agree?It is coherent' -> 'Do you agree? It is "+\
																"coherent'\n"+\
		"			'I agree!”' -> 'I agree!”' (same)\n"+\
		"			'I agree!!' -> 'I agree!!' (same)\n"+\
		"			'I agree?!' -> 'I agree?!' (same)\n"+\
		"			'I said to him:' -> 'I said to him:' (same) \n "
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if last_char in [u';',u':',u'!',u'?'] and \
											(next_char not in [u'\n',u' ']):
			if next_char== u'\u201d' or next_char== u'?' or next_char== u'!':
				return False
			if next_char== u'\u00A0':
				cursor.deleteChar()
			cursor.insertText(u' ')
			return True

		return False

class TLRuleEnglish0009 (TLRuleAbstract):
	number = 9
	title="A space or a newline after [.] or [,] except if it is a figure "+\
		"or a closing quoation mark [”] or another dot"
	description=	\
		"Check if there is a newline or a space after [.] or [,] and if it "+\
		"is not the case, it inserts one (replacing the non-breakable space "+\
		"is necessary. This rule does not apply if the next character is a "+\
		"figure.\n"+\
		"example :	'I agree.And you' -> 'I agree. And you'\n"+\
		"			'I agree,it is coherent' -> 'I agree, it is coherent'\n"+\
		"			'I agree.”' -> 'I agree.”' (same)\n"+\
		"			'The speed was 33.7 mph' -> 'The speed was 33.7 mph' (same)\n"+\
		"			'Let's see..' ->  'Let's see..' (same, the goal is to make an ellips)"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		ch_list = [u'\n',u' ',u'\u201d',u'.']+[str(i) for i in range(10)]
		if last_char in [u'.',u','] and (next_char not in ch_list):
			if next_char== u'\u00A0':
				cursor.deleteChar()
			cursor.insertText(u' ')
			return True

		return False

class TLRuleEnglish0010 (TLRuleAbstract):
	number = 10
	title="Replace the typewriter apostrophe by a curved apostrophe."
	description=	\
		"Replace a the char ['] by a curved apostrophe [’].\n\
		example :	'It's me' -> 'It’s me'"

	profile = 1
	def correct(self,last_char,next_char,cursor):
		if next_char==u"'":
			cursor.deleteChar()
			cursor.insertText(u'\u2019')
			return True
		return False

class TLRuleEnglish0011 (TLRuleAbstract):
	number = 11
	title="Replace 3 consecutive points by an ellipsis."
	description=	\
		"Replace 3 consecutive points into an ellipsis […]:\n\
		example :	'\"So...' -> 'So…'"
	profile = 1

	def correct(self,last_char,next_char,cursor):
		if last_char==u'.' and next_char==u'.':

			if self.language.lastChar(cursor,n=2)==u'.':
				cursor.deleteChar()
				cursor.deletePreviousChar()
				cursor.deletePreviousChar()
				cursor.insertText(u'\u2026')
				return True
		return False



language = Language(name="English",code="en",code_enchant="en_GB",
	afterCharRules=[TLRuleEnglish0001,
					TLRuleEnglish0002,
					TLRuleEnglish0003,
					TLRuleEnglish0004,
					TLRuleEnglish0005,
					TLRuleEnglish0006,
					TLRuleEnglish0007,
					TLRuleEnglish0008,
					TLRuleEnglish0009,
					TLRuleEnglish0010,
					TLRuleEnglish0011],
	delimiters = {
					'“':'“”',
					'"':"“”",
					'(':'()',
					'[':'[]',
					}

					)
