class TLRuleEnglish0001 (TLRuleAbstract):
	title="No space or non-breakable space before [,], [;], [:], [!], [?]"
	description=	\
		"Delete a space or an non-breakable space [⎵] before some "+\
		"ponctuation: [;], [:], [!], [?] or a closing quotes mark [”].\n"+\
		"example :	'Hello !' 		→ 'Hello!'\n"+\
		"			'Hello⎵!'		→ 'Hello!'\n"+\
		"			'Hello ;'	 	→ 'Hello;'\n"+\
		"			'Hello⎵;' 		→ 'Hello;'\n"+\
		"			'Hello :'		→ 'Hello:'\n"+\
		"			'Hello ?'		→ 'Hello?'\n"+\
		"			'Hello. ”'	→ 'Hello.”'"
	profile = 0

	def correct(self,last_char,next_char,cursor):
		if next_char in [u',',u';',u':',u'!',u'?',u'\201d']:
			if last_char==' ' or last_char==u'\u00A0':
				cursor.deletePreviousChar()
				return True
		return False


# class TLRuleEnglish0002 (TLRuleAbstract):
#
# 	title="A space or a newline after [;], [:], [!] or [?] except if it is a "+\
# 		"closing quotation mark [”] or [!], [?]"
# 	description=	\
# 		"Check if there is a newline or a space after [;], [:], [!] or [?] "+\
# 		"and if it is not the case, it inserts one (replacing the "+\
# 		"non-breakable space is necessary).\n"+\
# 		"example :	'I agree;and you' → 'I agree; and you'\n"+\
# 		"			'I agree:it is coherent' → 'I agree: it is coherent'\n"+\
# 		"			'I agree!It is coherent' → 'I agree! It is coherent'\n"+\
# 		"			'Do you agree?It is coherent' → 'Do you agree? It is "+\
# 																"coherent'\n"+\
# 		"			'I agree!”' → 'I agree!”' (same)\n"+\
# 		"			'I agree!!' → 'I agree!!' (same)\n"+\
# 		"			'I agree?!' → 'I agree?!' (same)\n"+\
# 		"			'I said to him:' → 'I said to him:' (same) \n "
# 	profile = 0
#
# 	def correct(self,last_char,next_char,cursor):
# 		if last_char in [u';',u':',u'!',u'?'] and \
# 											(next_char not in [u'\n',u' ']):
# 			if next_char== u'\u201d' or next_char== u'?' or next_char== u'!':
# 				return False
# 			if next_char== u'\u00A0':
# 				cursor.deleteChar()
# 			COTextCursorFunctions.insertText(cursor,u' ')
# 			return True
#
# 		return False




language = Language(name="English",code="en",code_enchant="en_GB",
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
					TLRuleEnglish0001,
					],
	delimiters = {
					'“':'“”',
					'"':"“”",
					'(':'()',
					'[':'[]',
					},
	quotes = ("“","”"),
	inside_quotes = None,
					)
