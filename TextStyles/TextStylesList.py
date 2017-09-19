from PyQt5 import QtGui, QtCore, QtWidgets
from .TextStylesPreferences import TSPreferences

# def problem with Ctrl+K


TSFontSizeAdjusmentDict={
	 "small" : 0 ,
	 "medium" : 1 ,
	 "large" : 2 ,
	 "x-large" : 3 ,
	 "xx-large" : 4 ,
	}

def getCharId(cursor):
	id = cursor.charFormat().property(QtGui.QTextFormat.UserProperty)
	# if id != None:
	# id = id.toPyObject()()
	return id

def getBlockId(cursor):
	if isinstance(cursor,QtGui.QTextBlock):
		cursor = QtGui.QTextCursor(cursor)
	id = cursor.blockFormat().property(QtGui.QTextFormat.UserProperty)
	# if id != None:
		# # id = id.toPyObject()()
	# id = id.toPyObject()()
	return id

class TSStyleClassAbstract:
	protected = False
	def __init__(self,constant=None,xmlMark=None,userPropertyId=None,name=None,
		shortcut=None,exportDict=None):
		"""
		- constant_name : the name of the constant style to consider
			It will be a dictionary with the following key-value :
			- char_style : 'italic' or 'bold' or 'underline'
			- font_name : 'times' or 'courrier' or all other font name
			- font_size : relative size of the font should be in
							{"small", "medium", "large", "x-large", "xx-large"}
			- font_color : a color in Qt.GlobalColor
		- xmlMark : the name to put into the xml sign
		- userPropertyId : the number that will represent the style
		- name : the name of the format, if by default ""
		- shortcut: the shortcut to apply to set the style
		- exportDict: the dictionnary to apply to make the exportation under
			the form: {"html":("<h1>","</h1>"),"txt":("==","==")}
		"""
		if name==None:
			name=""
		if constant==None: constant={}
		self.constant	 	= constant
		self.xmlMark 		= xmlMark
		self.userPropertyId = userPropertyId
		self.name			= name
		self.shortcut		= shortcut
		if exportDict==None: self.exportDict={}
		else: self.exportDict     = exportDict


	def inverseId(self,cursor):
		"""This function will reverse the userPropertyId
		Return res,cursor1:
			- res: True if we assigned the style, False if it has been removed.
			- cursor1: where the canges applied
		"""
		raise NotImplementedError

	def setStyleToQtFormating(self,qtFormating,document):
		"""This will apply the style to the corresponding qtFormat
		- qtCharFormat: either a QTextCharFormat or a QTextBlockFormat
		"""
		raise NotImplementedError

	def setIdFromXml(self,document):
		""" Will replace the XML elements of the text in the QTextEdit in the
		good userPropertyId """
		cursor_begin=QtGui.QTextCursor(document)
		cursor_begin.setPosition(0)

		# FIRST : we set the good format to what is inside the XML elements
		# Regular expression that will find the corresponding XML element :
		regexp_begin = QtCore.QRegExp('<'+self.xmlMark+'>')
		regexp_end   = QtCore.QRegExp('</'+self.xmlMark+'>')

		cursor_begin=document.find(regexp_begin,cursor_begin)
		while not cursor_begin.isNull():
			cursor_end = document.find(regexp_end,cursor_begin)
			if cursor_end.isNull():
				raise TSError("The open tag is not closed",cursor_begin.position())
			cursor_begin.setPosition(cursor_end.position(),QtGui.QTextCursor.KeepAnchor)
			res,cursor = self.inverseId(cursor_begin)
			assert res
			cursor_begin=document.find(regexp_begin,cursor_begin)
		# SECOND : we remove all the XML elements
		cursor=QtGui.QTextCursor(document)
		cursor.setPosition(0)
		while not cursor.isNull():
			cursor=document.find('<'+self.xmlMark+'>',cursor)
			cursor.deleteChar ()
			cursor=document.find('</'+self.xmlMark+'>',cursor)
			cursor.deleteChar ()

class TSStyleClassChar (TSStyleClassAbstract):
	"""A class that should be instanced with the corresponding glyphs in
	order to have the good format.
	"""
	def inverseId(self,cursor):
		"""Set or unset th id to the selection under the cursor.
		"""
		qtFormating = cursor.charFormat()
		id_ = getCharId(cursor)
		if id_ == self.userPropertyId:
			qtFormating.setProperty(QtGui.QTextFormat.UserProperty,None)
			res = False
		else:
			qtFormating.setProperty(QtGui.QTextFormat.UserProperty,
														self.userPropertyId)
			res = True
		cursor.setCharFormat(qtFormating)
		return res,cursor
		# def setStyleToQtFormating(self,qtFormating,document):
		# TSStyleClassChar.setStyleToQtFormatingStatic(qtFormating,
														# self.constant,document)
	def setStyleToQtFormating(self,qtFormating,document):
		"""
		- qtCharFormat: either a QTextCharFormat or a QTextBlockFormat
		"""

		for k,v in list(self.constant.items()):
			if k == 'char_style':
				if v == 'italic':
					qtFormating.setFontItalic(True)
				elif v == 'underline':
					qtFormating.setUnderlineStyle(
						QtGui.QTextCharFormat.SingleUnderline)
					qtFormating.setFontUnderline(True)
				elif v == 'bold':
					qtFormating.setFontWeight(QtGui.QFont.Bold)

			elif k == 'font_size':
				v = TSFontSizeAdjusmentDict[v]
				qtFormating.setProperty(QtGui.QTextFormat.FontSizeAdjustment,v)

			elif k == 'font_name':
				qtFormating.setProperty(QtGui.QTextFormat.FontFamily,v)

			elif k == 'font_color':
				try :
					color= QtGui.QColor(QtCore.Qt.__dict__[v])
				except KeyError as e:
					raise KeyError('Unknown color in QtCore.Qt.GlobalColor: '+\
							"'"+v+"'.")
				qtFormating.setForeground(color)

			else:
				raise ValueError("Unknown parameter for char formating :",k)
		qtFormating.setProperty(QtGui.QTextFormat.UserProperty,
														self.userPropertyId)


class TSStyleClassBlock (TSStyleClassAbstract):
	"""A class that should be instanced with the corresponding glyphs in
	order to have the good format.
	"""

	dict_align = {	'center': QtCore.Qt.AlignHCenter,
					'right':QtCore.Qt.AlignRight,
					'left':QtCore.Qt.AlignLeft,
					'justify':QtCore.Qt.AlignJustify}

	def __init__(self,*arg,**kargs):
		TSStyleClassAbstract.__init__(self,*arg,**kargs)
		constant_sub = self.constant.copy()
		for k,v in list(constant_sub.items()):
			if k == 'alignment':
				constant_sub.pop(k)
		self.subCharFormat = TSStyleClassChar(constant=constant_sub)

	def inverseId(self,cursor):
		"""Set or unset th id to the selection under the cursor.
		"""
		# [cursor.blockCharFormat(),cursor.blockFormat()]
		qtFormating =  cursor.blockFormat()
		id_ = getBlockId(cursor)
		if id_ == self.userPropertyId:
			qtFormating.setProperty(QtGui.QTextFormat.UserProperty,None)
			res = False
		else:
			qtFormating.setProperty(QtGui.QTextFormat.UserProperty,
														self.userPropertyId)
			res = True
		cursor.setBlockFormat(qtFormating)
		return res,cursor


	def setStyleToQtFormating(self,qtFormating,document):
		assert type(qtFormating)==list
		constants = self.constant.copy()
		qtFormating0 = qtFormating[0]
		for k,v in list(self.constant.items()):
			if k == 'alignment':
				qtFormating0.setProperty(QtGui.QTextFormat.BlockAlignment,
															self.dict_align[v])
			qtFormating0.setProperty(QtGui.QTextFormat.UserProperty,
													self.userPropertyId)
		if len(qtFormating)>=2:
			qtFormating1 = qtFormating[1]
			self.subCharFormat.setStyleToQtFormating(qtFormating1,document)


class TSStyleClassSeparator (TSStyleClassBlock):
	"""Will deal with the separator class"""
	protected = True

	def inverseId(self,cursor):
		"""
		Return res,cursor1:
			- res: True if we assigned the style, False if it has been removed.
			- cursor1: where the changes applies
		"""
		id_ = getBlockId(cursor)
		if id_ != self.userPropertyId:
			if cursor.hasSelection() :
				cursor.removeSelectedText()
			if cursor.block().text().strip()!='':
				cursor.insertBlock()
			cursor.insertText(TSPreferences['SEPARATOR_MOTIF'])
			pos = cursor.position()
			if cursor.atEnd() or (not cursor.atBlockEnd()):
				cursor.insertBlock()
			cursor.setPosition(pos,QtGui.QTextCursor.MoveAnchor)
			res,cursor = TSStyleClassBlock.inverseId(self,cursor)
			cursor1 = QtGui.QTextCursor(cursor)
			cursor.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.MoveAnchor)
			return res,cursor1
		else:
			cursor.select(QtGui.QTextCursor.BlockUnderCursor)
			cursor.deleteChar()
			res = False
			return res, cursor


	def setIdFromXml(self,document):
		""" Will replace the XML elements of the text in the QTextEdit in the
		good formating (for now, only work with emphasize) """
		cursor=QtGui.QTextCursor(document)
		cursor.setPosition(0)

		# Regular expression that will find the corresponding XML element :
		# regexp = QtCore.QRegExp(r'[\n]?<'+self.xmlMark+r'/>[\n]?')# TODO
		exp = r'<'+self.xmlMark+r'/>'# TODO
		cursor=document.find(exp,cursor)
		while not cursor.isNull():
			cursor1 = QtGui.QTextCursor(document)
			cursor1.setPosition(cursor.selectionStart())
			if cursor1.atBlockStart():
				cursor1.movePosition(QtGui.QTextCursor.Left,
						QtGui.QTextCursor.MoveAnchor)
			cursor1.setPosition(cursor.selectionEnd(),
					QtGui.QTextCursor.KeepAnchor)
			if cursor1.atBlockEnd():
				cursor1.movePosition(QtGui.QTextCursor.Right,
						QtGui.QTextCursor.KeepAnchor)

			self.inverseId(cursor1)

			cursor=document.find(exp,cursor)


class TSStyleClassImage (TSStyleClassBlock):
	protected = True
	def inverseId(self,cursor):
		# cursor1 = QtGui.QTextCursor(cursor)
		# qtFormating = self.getQtFormating(cursor1)
		id_ = getBlockId(cursor)
		if id_ != self.userPropertyId:
			if cursor.hasSelection() :
				cursor.clearSelection()
			if cursor.block().text().strip()!='':
				cursor.insertBlock()
			# cursor.insertText(TSPreferences['SEPARATOR_MOTIF'])
			pos = cursor.position()
			if cursor.atEnd() or (not cursor.atBlockEnd()):
				cursor.insertBlock()
			cursor.setPosition(pos,QtGui.QTextCursor.MoveAnchor)

			res,cursor = TSStyleClassBlock.inverseId(self,cursor)

			cursor1 = QtGui.QTextCursor(cursor)
			cursor.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.MoveAnchor)
			res = True
			return res,cursor1

		else:
			cursor.select(QtGui.QTextCursor.BlockUnderCursor)
			cursor.deleteChar()
			res = False

		# pass
		# if res:
			# cursor.insertText(TSPreferences['SEPARATOR_MOTIF']+'\n')

		return res,cursor

TSStyleEmphasize = TSStyleClassChar(
	constant		=  TSPreferences['EMPHASIZE_STYLE'],
	xmlMark			=  'e',
	userPropertyId	=  1,
	name			=  'Emphasize',
	shortcut		=  'Ctrl+E',
	exportDict		=  {	'txt'  :('*','*'),
							'html' :('<em>', '</em>') ,
							'tex':(r'\emph{',r'}'),
							'mkd':('*','*'),
						}
	)


TSStyleSeparator = TSStyleClassSeparator(
	constant		=  TSPreferences['SEPARATOR_STYLE'],
	xmlMark			=  'sep',
	userPropertyId	=  2,
	name			=  'Separator',
	shortcut		=  'Ctrl+K',
	exportDict		=  {	'txt'  :('***',''),
							'html' :('<h4><center>***</center></h4>',''),
							'tex':('\\begin{center}\n***\n\\end{center}',''),
							'mkd':('***',''),
						}
	)

TSStyleHeader1 = TSStyleClassBlock(
	constant		=  TSPreferences['HEADER1_STYLE'],
	xmlMark			=  'h1',
	userPropertyId	=  3,
	name			=  'Header 1',
	shortcut		=  'Ctrl+1',
	exportDict		=  {	'txt'  :('==','=='),
							'html' :('<h1>','</h1>'),
							'tex':(r'\section*{','}'),
							'mkd':('# ',''),
						}
	)

TSStyleHeader2 = TSStyleClassBlock(
	constant		=  TSPreferences['HEADER2_STYLE'],
	xmlMark			=  'h2',
	userPropertyId	=  4,
	name			=  'Header 2',
	shortcut		=  'Ctrl+2',
	exportDict		=  {	'txt'  :('===','==='),
							'html' :('<h2>','</h2>'),
							'tex':(r'\subsection*{','}'),
							'mkd':('## ',''),
						}
	)

TSStyleHeader3 = TSStyleClassBlock(
	constant		=  TSPreferences['HEADER3_STYLE'],
	xmlMark			=  'h3',
	userPropertyId	=  5,
	name			=  'Header 3',
	shortcut		=  'Ctrl+3',
	exportDict		=  {	'txt'  :('====','===='),
							'html' :('<h3>','</h3>'),
							'tex':(r'\subsubsection*{','}'),
							'mkd':('### ',''),
						}
	)



TSStyleCode = TSStyleClassBlock(
	constant		=  TSPreferences['CODE_STYLE'],
	xmlMark			=  'code',
	userPropertyId	=  6,
	name			=  'Code',
	# shortcut		=  'Ctrl+R',
	shortcut		=  '',
	exportDict		=  {	'txt'  :('>>> ',''),
							'html' :('>>> ',''),
							'tex'  :('>>> ',''),
							'mkd'  :('```','```'),
						}
	)

TSStylePhantom = TSStyleClassBlock(
	constant		=  TSPreferences['PHANTOM_STYLE'],
	xmlMark			=  'phantom',
	userPropertyId	=  7,
	name			=  'Phantom',
	shortcut		=  'Ctrl+R',
	exportDict		=  {	'txt'  :('[[[',']]]'),
							'html' :(' <font color="gray">','</font>'),
							'tex'  :(r'{\tiny ','}'),
							'mkd' :(' <font color="gray">','</font>'),
						}
	)

TSStyleImage =  TSStyleClassImage(
	constant		=  TSPreferences['IMAGE_STYLE'],
	xmlMark			=  'img',
	userPropertyId	=  8,
	name			=  'Image',
	# shortcut		=  'Ctrl+R',
	exportDict		=  {
							'txt'  :('[[File:',']]'),
							'html' :('<center><img src="','" width="685" /></img></center>'),
							'tex'  :(r'\begin{center}\includegraphics[width=10cm]{','}\end{center}'),
							'mkd' :('![image](',')'),
						}
	)


TSStyleStyleColor1 = TSStyleClassChar(
	constant		=  TSPreferences['COLOR1_STYLE'],
	xmlMark			=  'span1',
	userPropertyId	=  101,
	name			=  'Color1',
	shortcut		=  'Ctrl+P+3',
	exportDict		=  {	'txt'  :('>',''),
							'html' :('<span style="color:#0000FF"> ','</span>'),
							'tex':(r'{\color{blue} ','}'),
							'mkd':('<span style="color:#0000FF"> ','</span>'),
						}
	)

TSStyleStyleColor2 = TSStyleClassChar(
	constant		=  TSPreferences['COLOR2_STYLE'],
	xmlMark			=  'span2',
	userPropertyId	=  102,
	name			=  'Color2',
	shortcut		=  '',
	exportDict		=  {	'txt'  :('>>',''),
							'html' :('<span style="color:#FF0000"> ','</span>'),
							'tex':(r'{\color{red} ','}'),
							'mkd':('<span style="color:#FF0000"> ','</span>'),
						}
	)

TSStyleStyleColor3 = TSStyleClassChar(
	constant		=  TSPreferences['COLOR3_STYLE'],
	xmlMark			=  'span3',
	userPropertyId	=  103,
	name			=  'Color3',
	shortcut		=  '',
	exportDict		=  {	'txt'  :('>>>',''),
							'html' :('<span style="color:#00FF00"> ','</span>'),
							'tex':(r'{\color{green} ','}'),
							'mkd':('<span style="color:#00FF00"> ','</span>'),
						}
	)
