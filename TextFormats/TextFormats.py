from PyQt4 import QtGui, QtCore
import copy

from TextFormatsConstants import TFConstants
from TextFormatsList import *


class TFFormatClassManager:
	"""This class will manage all the format either the bloc of the char 
	ones."""
	def __init__(self,listBlockFormat,listCharFormat,textedit=None):
		"""
		- listBlockFormat : the list of the TFFormatClassBloc instances
		- listCharFormat : the list of the TFFormatClassChar instances
		"""
		self.listCharFormat = listCharFormat
		self.listBlockFormat = listBlockFormat
		
		
		self.dictCharFormat = {f.userPropertyId:f for f in listCharFormat} 
		self.dictBlockFormat = {f.userPropertyId:f for f in listBlockFormat} 
		self.dictFormat = {f.userPropertyId:f for f in \
										listCharFormat+listBlockFormat} 
		
		self.textedit = textedit
		
		#bloc format at first then char format
	
	# def addFormat(self,format):
	# 	"""
	# 	Function used to add formats to the lists
	# 	"""
	# 	if isinstance(format,TFFormatClassChar):
	# 		self.listCharFormat.append(format)
	# 	elif isinstance(format,TFFormatClassBlock):
	# 		self.listBlockFormat.append(format)
	# 	else:
	# 		raise ValueError("format sould be a TFFormatClassBloc or a "+\
	# 			"TFFormatClassBloc instance, here it is "+str(type(fromat)))
	# 	format.formatManager=self
		
		
	def toXml(self,plaintext,document):
		"""Will return the text of the document with the XML balises for each
		format.
		"""
		newText=plaintext[:]
		place_to_mark = self.get_place_to_mark(document)
					
		# We add the XML elements in the string
		gap=0 # the gap between the old and the new newText indexing
		for pos,entry in place_to_mark:
			newText = newText[:pos+gap]+entry+newText[pos+gap:]
			gap+=len(entry)
		
		newText=unicode(newText)
		# We remove the TFConstants['SEPARATOR_MOTIF']
		for format in self.listBlockFormat: 
			if isinstance(format,TFFormatClassSeparator):
				
				newText = newText.replace(
					'<'+format.xmlMark+'>'+TFConstants['SEPARATOR_MOTIF']+\
													'</'+format.xmlMark+'>',
					'<'+format.xmlMark+'/>')
				break
		return newText
	
	def get_place_to_mark(self,document):
		"""
		Will return a list of where to put the mark in the document :
		- document: the QTextDocument on to perform the position
		[(pos1,element1),(pos2,element2),...]
		"""
		
		format_char_structure=[] # the form will be:
					# [  [format1,start_element_1,stop_element_1],
					#    [format2,start_element_2,stop_element_2],...  ]
		format_block_structure=[] # the form will be:
					# [  [format1,start_element_1,stop_element_1],
					#    [format2,start_element_2,stop_element_2],...  ]
					
		# We search the place where are the formats elements 
		
		block = document.firstBlock()
		while block.blockNumber ()  >=0 : #because if empty block, its number
													# is -1
			cursor=QtGui.QTextCursor(block)
			
			qtBlockFormat = cursor.blockFormat()
			userId = qtBlockFormat.property(QtGui.QTextFormat.UserProperty)
			userId = userId.toPyObject()
			if userId!=None and self.dictBlockFormat.has_key(userId):
				# if the format exists
				format = self.dictBlockFormat[userId]
				format_block_structure.append(
					[	format,
						cursor.position(),
						cursor.position()+cursor.block().length()-1
					]
					)
					
			# cursor.movePosition(QtGui.QTextCursor.Right)
			while not cursor.atBlockEnd():
				cursor.movePosition(QtGui.QTextCursor.Right)
				qtCharFormat = cursor.charFormat()
				userId = qtCharFormat.property(QtGui.QTextFormat.UserProperty)
				userId = userId.toPyObject()
				
				if self.dictCharFormat.has_key(userId):
				# 	format = self.dictCharFormat[userId]
				# 	# if cursor.atBlockStart()
				# 		# pos = cursor.position()
				# 	# else :
				# 	#if the format corresponds
				# 	if len(format_char_structure)==0: 
				# 		#if it is the first element of the list
				# 		format_char_structure.append([format,cursor.position()-1,
				# 							  cursor.position()])
				# 	elif 	(not cursor.atBlockStart()) and \
				# 			format==format_char_structure[-1][0] and \
				# 			format_char_structure[-1][-1]==cursor.position(): 
				# 		# if we are not at the begining of a new paragraph
				# 		# and the previous char was already under the same 
				# 		# format:
				# 		format_char_structure[-1][-1]+=1
				# 		
				# 	else: #if it is a new element
				# 		format_char_structure.append([format,cursor.position(),
				# 							  cursor.position()+1])

					#if the format corresponds
					format = self.dictCharFormat[userId]
					pos = cursor.position()
					
					if 		len(format_char_structure)==0 or \
							format != format_char_structure[-1][0] or \
							pos  != format_char_structure[-1][-1]+1:
						# if it is the first element of the list or the 
						# previous char was not already under the same format:
						format_char_structure.append( [format,pos-1,pos] )
						
					else :
						# if the previous char was already under the same 
						# format:
						format_char_structure[-1][-1] += 1

				
			block = block.next()
		# We search the place where to put the XML elements in the final 
		# string:
		d = {}
		for format,start,end in format_char_structure:
			d[start] = d.get(start,'')+'<'+format.xmlMark+'>' 
			assert not d.has_key(end)
			d[end] = '</'+format.xmlMark+'>' 
		for format,start,end in format_block_structure :
			# if isinstance(format,TFFormatClassSeparator):
			# 	d[start] = '\n<'+format.xmlMark+'/>' + d.get(start,'') 
			# else : 
			d[start] = '<'+format.xmlMark+'>' + d.get(start,'') 
			d[end] =  d.get(end,'') + '</'+format.xmlMark+'>' 
		list_keys = d.keys()
		list_keys.sort()
		place_to_mark = [(i,d[i]) for i in list_keys]
		return place_to_mark
		
		
	def fromXml(self,document):
		"""Will replace the XML elements of the text in the QTextEdit in the 
		good formating (for now, only work with emphasize) """
		for blocFormat in self.listBlockFormat:
			blocFormat.setFormatFromXml(document)
		for charFormat in self.listCharFormat:
			charFormat.setFormatFromXml(document)
			
	def setCharFormatsToBlock(self,block):
		"""When removing a block format, we have to check that the char 
		formating of the block is indeed well."""
		cursor = QtGui.QTextCursor(block)
		while not cursor.atBlockEnd ():
			cursor.movePosition(QtGui.QTextCursor.Right,
										QtGui.QTextCursor.KeepAnchor)
			qtCharFormat = cursor.charFormat()
			qtCharFormat_id = qtCharFormat.property(
										QtGui.QTextFormat.UserProperty)
			if qtCharFormat_id != None:
				qtCharFormat_id = qtCharFormat_id.toPyObject()
			# qtCharFormat_id = qtCharFormat_id.toPyObject()
			if qtCharFormat_id  in self.dictCharFormat.keys():
				format = TFFormatManager.dictCharFormat[qtCharFormat_id]
				format.setStyleToQtFormating(qtCharFormat,cursor.document())
				format.setQtFormating(cursor,qtCharFormat)
				
			cursor.clearSelection()
			
	def setBlockFormatsToChar(self,cursor):
		"""When removing a char format, we have to check that the block
		formating is indeed well."""
		qtBlockFormat = cursor.blockFormat()
		qtCharFormat = cursor.charFormat()
		qtBlockFormat_id = qtBlockFormat.property(
												QtGui.QTextFormat.UserProperty)
		qtBlockFormat_id = qtBlockFormat_id.toPyObject()
		
		if qtBlockFormat_id in self.dictBlockFormat.keys():
			format = TFFormatManager.dictBlockFormat[qtBlockFormat_id]
			format.setStyleToQtFormating([qtCharFormat,qtBlockFormat])
			format.setQtFormating(cursor,[qtCharFormat,qtBlockFormat])
		
			
			
	def inverseFormat(self,cursor,format_id):
		if format_id in self.dictBlockFormat.keys():
			res = self.dictBlockFormat[format_id].inverseFormat(cursor)
			if not res:
				self.setCharFormatsToBlock(cursor.block())
		elif format_id in self.dictCharFormat.keys():
			res = self.dictCharFormat[format_id].inverseFormat(cursor)
			if not res:
				self.setBlockFormatsToChar(cursor)
		else:
			raise ValueError('Format id '+str(format_id)+' unknown !')
			
		
# 	def setFormatsToBlocOLD(self,block):
# 		########## OLD
# 		"""Will set the good formating for the given block """
# 		def getDefaultFormat(id=None,char=True):
# 			print "Old, we should not pass there"
# 			if char :
# 				qtFormat = QtGui.QTextCharFormat(
# 											self.textedit.defaultCharFormat)
# 			else:
# 				qtFormat = QtGui.QTextBlockFormat(
# 											self.textedit.defaultBlockFormat)
# 			qtFormat.setProperty(QtGui.QTextFormat.UserProperty,id)
# 			return qtFormat
# 			
# 		# We set the good format to the block :
# 		qtBlockFormat_id = block.blockFormat().property(
# 											QtGui.QTextFormat.UserProperty)
# 		qtBlockFormat_id = qtBlockFormat_id.toPyObject()
# 		qtBlockFormat = getDefaultFormat(qtBlockFormat_id,char=False)
# 		qtBlockCharFormat  = getDefaultFormat()
# 		
# 		if qtBlockFormat_id  in TFFormatManager.dictBlocFormat.keys():
# 			# if it is a bloc with a known ID :
# 			format = TFFormatManager.dictBlocFormat[qtBlocFormat_id]
# 			
# 			self.setStyleToQtFormat(qtBlockFormat, format)
# 			
# 			self.setStyleToQtFormat(qtBlockCharFormat,format)
# 			
# 		cursor = QtGui.QTextCursor(block)
# 		cursor.select(QtGui.QTextCursor.BlockUnderCursor)
# 		cursor.setBlockFormat(qtBlockFormat)
# 		# cursor.setCharFormat(qtCharFormat)
# 		
# 		# We set the good format to the chars		
# 		# for format in TFFormatManager.listBlockFormat + \
# 				# TFFormatManager.listCharFormat:
# 		cursor = QtGui.QTextCursor(block)
# 		while not cursor.atBlockEnd ():
# 			print 'cursor.positionInBlock() : ',cursor.positionInBlock()
# 			cursor.movePosition(QtGui.QTextCursor.Right,
# 										QtGui.QTextCursor.KeepAnchor)
# 			qtCharFormat = cursor.charFormat()
# 			qtCharFormat_id = qtCharFormat.property(
# 										QtGui.QTextFormat.UserProperty)
# 			qtCharFormat_id = qtCharFormat_id.toPyObject()
# 			print 'qtCharFormat_id : ',qtCharFormat_id
# 			if qtCharFormat_id  in TFFormatManager.dictCharFormat.keys():
# 				format = TFFormatManager.dictCharFormat[qtCharFormat_id]
# 				qtCharFormatNew = QtGui.QTextCharFormat(qtBlockCharFormat)
# 				self.setStyleToQtFormat(qtCharFormatNew,format)
# 				cursor.setCharFormat(qtCharFormatNew)
# 			else : 
# 				cursor.setCharFormat(qtBlockCharFormat)
# 				
# 			cursor.clearSelection()
# 			
# 		print '==after=='
# 		cursor = QtGui.QTextCursor(block)
# 		while not cursor.atBlockEnd ():
#			print 'cursor.positionInBlock() : ',cursor.positionInBlock()
# 			print 'qtCharFormat_id : ',qtCharFormat_id	
# 			cursor.movePosition(QtGui.QTextCursor.Right,
# 										QtGui.QTextCursor.MoveAnchor)
# 			
# 	def setStyleToQtFormat(self,qtFormat,format):
# 	
# 		for k,v in format.constant.items():
# 			if k == 'char_style':
# 				if v == 'italic':
# 					qtFormat.setFontItalic(True)
# 				if v == 'underline':
# 					qtFormat.setFontItalic(True)
# 		qtFormat.setProperty(QtGui.QTextFormat.UserProperty,
# 													format.userPropertyId)			
				
		

# TFFormatEmphasize = TFFormatClassChar('EMPHASIZE_STYLE',     'e'  ,1,'Ctrl+E')
# TFFormatSeparator = TFFormatClassSeparator('SEPARATOR_STYLE','sep',2,'Ctrl+K')
# TFFormatHeader1 = TFFormatClassBlock('HEADER1_STYLE','h1',3,'Ctrl+1')
# TFFormatHeader2 = TFFormatClassBlock('HEADER2_STYLE','h2',4,'Ctrl+2')
# TFFormatHeader3 = TFFormatClassBlock('HEADER3_STYLE','h3',5,'Ctrl+3')
TFFormatManager = TFFormatClassManager(
	listBlockFormat = [	TFFormatSeparator,TFFormatHeader1,
						TFFormatHeader2,TFFormatHeader3,TFFormatCode],
	listCharFormat = [TFFormatEmphasize])
#TFFormatsList=[TFFormatEmphasize,TFFormatSeparator]		
	