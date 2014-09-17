from PyQt4 import QtGui, QtCore
from TextFormatsConstants import TFConstants,TFError


class TFFormatClassAbstract:
	protected = False
	def __init__(self,constant_name,xmlMark,userPropertyId,shortcut=None,
		exportDict=None):
		"""
		- constant_name : the name of the constant style to consider 
			It will be a dictionary with the following key-value :
			- char_style : 'italic' or 'bold' or 'underline'
			- char_color : 'black' or 'red' or 'blue' or all other colours of 
				Qt
			- font_name : 'times' or 'courrier' or all other font name
			- font_size : "10" or all other string that represent an int
		- xmlMark : the name to put into the xml sign
		- userPropertyId : the number that will represent the style
		- shortcut: the shortcut to apply to set the style
		- exportDict: the dictionnary to apply to make the exportation under 
			the form: {"html":("<h1>","</h1>"),"txt":("==","==")}
		"""
		self.constant_name 	= constant_name
		self.constant	 	= TFConstants[constant_name]
		self.xmlMark 		= xmlMark
		self.userPropertyId = userPropertyId
		self.shortcut		= shortcut
		if exportDict==None: self.exportDict={}
		else: self.exportDict     = exportDict

	def inverseFormat(self,cursor):
		"""Will inverse the userPropertyId in the selection of the cursor. 
		- format : the current Qt format
		- formatSet : the function that will set the UserPropertyID
		return :
		- True if we set the userPropertyId
		- False if we remove the userPropertyId"""
		qtFormating = self.getQtFormating(cursor)
		id_ = self.getId(cursor)
		
		if id_ == self.userPropertyId:
			self.setInverseStyleToQtFormating (qtFormating,cursor.document())
			self.setQtFormating(cursor,qtFormating)
			self.setId(cursor,qtFormating, unset=True)
			res = False
		else:
			self.setStyleToQtFormating (qtFormating,cursor.document())
			self.setQtFormating(cursor,qtFormating)
			self.setId(cursor,qtFormating)
			res = True
			
		return res	


	def setFormatFromXml(self,document):
		""" Will replace the XML elements of the text in the QTextEdit in the 
		good formating (for now, only work with emphasize) """
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
				raise TFError("The open tag is not closed",cursor_begin.position())
			cursor_begin.setPosition(cursor_end.position(),QtGui.QTextCursor.KeepAnchor)
			res = self.inverseFormat(cursor_begin)
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

	def setStyleToQtFormating(self,qtFormating):
		raise NotImplementedError
	

	def setInverseStyleToQtFormating(self,qtFormating,document):
		raise NotImplementedError

		
	def getId(self,cursor):
		"""Get the format id under the cursor (either the block or the char 
		id)"""
		raise NotImplementedError

	def setId(self,cursor,qtFormating,unset=False):
		"""Set the good id to the selection under the cursir (either the block 
		or the char id).
		- unset: if True, the id will be set to None, otherwise, it will take
			the self.userPropertyId.
		"""
		raise NotImplementedError

	def getQtFormating(self,cursor):
		raise NotImplementedError

	def setQtFormating(self,cursor,qtFormating):
		raise NotImplementedError


class TFFormatClassChar (TFFormatClassAbstract):
	"""A class that should be instanced with the corresponding glyphs in 
	order to have the good format.	
	"""
	@staticmethod
	def setStyleToQtFormatingStatic(qtFormating,constants,document):
		for k,v in constants.items():
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
				v= int(v)
				qtFormating.setProperty(QtGui.QTextFormat.FontPointSize,v)		
				
			elif k == 'font_name':
				qtFormating.setProperty(QtGui.QTextFormat.FontFamily,v)		
				
			else:
				raise ValueError("Unknown parameter for char formating :",k)

	@staticmethod
	def setInverseStyleToQtFormatingStatic(qtFormating,constants,document):
		for k,v in constants.items():
			if k == 'char_style':
				if v == 'italic':
					italic = document.defaultFont () .italic()
					qtFormating.setProperty(QtGui.QTextFormat.FontItalic,
																		italic)
				elif v == 'underline':
					underline = document.defaultFont () .underline()
					qtFormating.setProperty(
						QtGui.QTextFormat.TextUnderlineStyle,underline)
				elif v == 'bold':
					weight = document.defaultFont () .weight ()
					qtFormating.setProperty(QtGui.QTextFormat.FontWeight,
																		weight)
			
			elif k == 'font_size':
				pointSize = 	document.defaultFont () .pointSize ()
				qtFormating.setProperty(QtGui.QTextFormat.FontPointSize,
																	pointSize)
			elif k == 'font_name':
				fontName = 	document.defaultFont () .family ()
				qtFormating.setProperty(QtGui.QTextFormat.FontFamily,
																	fontName)
			
			else:
				raise ValueError("Unknown parameter for char formating :",k)
	
	
	def setStyleToQtFormating(self,qtFormating,document):
		TFFormatClassChar.setStyleToQtFormatingStatic(qtFormating,
														self.constant,document)
	

	def setInverseStyleToQtFormating(self,qtFormating,document):
		TFFormatClassChar.setInverseStyleToQtFormatingStatic(qtFormating,
													self.constant,document)
				
				
	def getId(self,cursor):
		"""Get the format id under the cursor (either the block or the char 
		id)"""
		return cursor.charFormat().property(QtGui.QTextFormat.UserProperty)

	def setId(self,cursor,qtFormating,unset=False):
		"""Set the good id to the selection under the cursir (either the block 
		or the char id).
		- unset: if True, the id will be set to None, otherwise, it will take
			the self.userPropertyId.
		"""
		if unset : id_ = None
		else: id_ = self.userPropertyId
		
		qtFormating.setProperty(QtGui.QTextFormat.UserProperty,id_)
		cursor.setCharFormat(qtFormating)
	
	def getQtFormating(self,cursor):
		return  cursor.charFormat()

	def setQtFormating(self,cursor,qtFormating):
		cursor.setCharFormat(qtFormating)


	
class TFFormatClassBlock (TFFormatClassAbstract):
	"""Will deal with the format to apply on the whole bloc (for titles f.i.)
	"""
	def setStyleToQtFormating(self,qtFormating,document):
		assert type(qtFormating)==list
		constants = self.constant.copy()
		qtFormating0 = qtFormating[0]
		qtFormating1 = qtFormating[1]
		if 'alignment' in self.constant.keys():
			v = self.constant['alignment']
			if v == 'center':
				qtFormating1.setProperty(QtGui.QTextFormat.BlockAlignment,
													QtCore.Qt.AlignHCenter)
			elif v == 'right':
				qtFormating1.setProperty(QtGui.QTextFormat.BlockAlignment,
													QtCore.Qt.AlignRight)
			elif v == 'left':
				qtFormating1.setProperty(QtGui.QTextFormat.BlockAlignment,
													QtCore.Qt.AlignLeft)
			elif v == 'justify':
				qtFormating1.setProperty(QtGui.QTextFormat.BlockAlignment,
													QtCore.Qt.AlignJustify)
			else:
				raise KeyError('Unknown value '+v+\
												' for the option "alignement"')
			constants.pop('alignment')
		else:
			alignment= document.defaultTextOption().alignment ()
			qtFormating1.setProperty(QtGui.QTextFormat.BlockAlignment,
													alignment)
		
		TFFormatClassChar.setStyleToQtFormatingStatic(qtFormating0,constants,
																	document)
		

	def setInverseStyleToQtFormating(self,qtFormating,document):
		assert type(qtFormating)==list
		constants = self.constant.copy()
		qtFormating0 = qtFormating[0]
		qtFormating1 = qtFormating[1]
		for k,v in self.constant.items():
			if k == 'alignment':
				alignment= document.defaultTextOption().alignment ()
				qtFormating1.setProperty(QtGui.QTextFormat.BlockAlignment,
														alignment)
				constants.pop(k)
				
		TFFormatClassChar.setInverseStyleToQtFormatingStatic(qtFormating0,
														constants,document)

		
	def getId(self,cursor):
		"""Get the format id under the cursor (either the block or the char 
		id)"""
		return cursor.blockFormat().property(QtGui.QTextFormat.UserProperty)
		
	def setId(self,cursor,qtFormating,unset=False):
		"""Set the good id to the selection under the cursir (either the block 
		or the char id).
		- unset: if True, the id will be set to None, otherwise, it will take
			the self.userPropertyId.
		"""
		if unset : id_ = None
		else: id_ = self.userPropertyId
		
		qtFormating = cursor.blockFormat()
		qtFormating.setProperty(QtGui.QTextFormat.UserProperty,id_)
		cursor.setBlockFormat(qtFormating)

	def getQtFormating(self,cursor):
		return  [cursor.blockCharFormat(),cursor.blockFormat()]

	def setQtFormating(self,cursor,qtFormating):
		assert type(qtFormating)==list
		cursor.setBlockFormat(qtFormating[1])
		cursor = QtGui.QTextCursor(cursor)
		cursor.select(QtGui.QTextCursor.BlockUnderCursor)
		cursor.setBlockCharFormat(qtFormating[0])
		cursor.mergeCharFormat(qtFormating[0])


		

class TFFormatClassSeparator (TFFormatClassBlock):
	"""Will deal with the separator class"""
	protected = True
	def inverseFormat(self,cursor):
		qtFormating = self.getQtFormating(cursor)
		id_ = self.getId(cursor)
		if id_ != self.userPropertyId:
			cursor.insertBlock()
			res = TFFormatClassBlock.inverseFormat(self,cursor)
			cursor.insertText(TFConstants['SEPARATOR_MOTIF']+'\n')
			
			id_ = self.getId(cursor)
			if id_ == self.userPropertyId:
				res = TFFormatClassBlock.inverseFormat(self,cursor)
		else:
			cursor.select(QtGui.QTextCursor.BlockUnderCursor)
			cursor.deleteChar()
		
		# if res:
			# cursor.insertText(TFConstants['SEPARATOR_MOTIF']+'\n')
			
		# return res
	
	# def setQtFormating(self,cursor,qtFormating):
		# assert type(qtFormating)==list
		# cursor.insertBlock ( qtFormating[1], qtFormating[0])
		# cursor.insertText(TFConstants['SEPARATOR_MOTIF']+'\n')
		
	
	def setFormatFromXml(self,document):
		""" Will replace the XML elements of the text in the QTextEdit in the 
		good formating (for now, only work with emphasize) """
		cursor=QtGui.QTextCursor(document)
		cursor.setPosition(0)
		
		# Regular expression that will find the corresponding XML element :
		# regexp = QtCore.QRegExp(r'[\n]?<'+self.xmlMark+r'/>[\n]?')# TODO
		exp = r'<'+self.xmlMark+r'/>'# TODO
		print 'exp : ',exp
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
			
			self.inverseFormat(cursor1)
			
			cursor=document.find(exp,cursor)	
		
# constant_name	=  ,
# xmlMark			=  ,
# userPropertyId	=  ,
# shortcut		=  ,
# exportDict		=  ,

TFFormatEmphasize = TFFormatClassChar(
	constant_name	=  'EMPHASIZE_STYLE',
	xmlMark			=  'e',
	userPropertyId	=  1,
	shortcut		=  'Ctrl+E',
	exportDict		=  {	'txt'  :('*','*'),
							'html' :('<i>', '</i>') ,
							'tex':(r'\emph{',r'}'),
						}
	)


TFFormatSeparator = TFFormatClassSeparator(
	constant_name	=  'SEPARATOR_STYLE',
	xmlMark			=  'sep',
	userPropertyId	=  2,
	shortcut		=  'Ctrl+K',
	exportDict		=  {	'txt'  :('***',''),
							'html' :('<h4><center>***</center></h4>',''),
							'tex':('\\begin{center}\n***\n\\end{center}',''),
						}
	)

TFFormatHeader1 = TFFormatClassBlock(
	constant_name	=  'HEADER1_STYLE',
	xmlMark			=  'h1',
	userPropertyId	=  3,
	shortcut		=  'Ctrl+1',
	exportDict		=  {	'txt'  :('==','=='),
							'html' :('<h1>','</h1>'),
							'tex':(r'\section*{','}'),
						}
	)

TFFormatHeader2 = TFFormatClassBlock(
	constant_name	=  'HEADER2_STYLE',
	xmlMark			=  'h2',
	userPropertyId	=  4,
	shortcut		=  'Ctrl+2',
	exportDict		=  {	'txt'  :('===','==='),
							'html' :('<h2>','</h2>'),
							'tex':(r'\subsection*{','}'),
						}
	)
	
TFFormatHeader3 = TFFormatClassBlock(
	constant_name	=  'HEADER3_STYLE',
	xmlMark			=  'h3',
	userPropertyId	=  5,
	shortcut		=  'Ctrl+3',
	exportDict		=  {	'txt'  :('====','===='),
							'html' :('<h3>','</h3>'),
							'tex':(r'\subsubsection*{','}'),
						}
	)
	
TFFormatCode = TFFormatClassBlock(
	constant_name	=  'CODE_STYLE',
	xmlMark			=  'code',
	userPropertyId	=  6,
	shortcut		=  'Ctrl+R',
	exportDict		=  {	'txt'  :('>>> ',''),
							'html' :('>>> ',''),
							'tex'  :('>>> ',''),
						}
	)
	