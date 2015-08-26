from PyQt4 import QtGui, QtCore
import copy

from TextStylesConstants import TSConstants
from TextStylesList import *


	
def yieldBlock(cursor):
	"""return [block, cursor_with_selection]
	- direction : if positive, then will go forward otherwise, it will go 
			backward.
	"""
	
	pos1=cursor.selectionStart()
	pos2=cursor.selectionEnd ()
	
	if pos1>pos2:
		tmp = pos1
		pos1=pos2
		pos2=tmp

	startCursor=QtGui.QTextCursor(cursor)
	endCursor=QtGui.QTextCursor(cursor)
	startCursor.setPosition(pos1)
	endCursor  .setPosition(pos2)
	
	while 	startCursor.blockNumber()<endCursor.blockNumber():
		bl = startCursor.block()
		startCursor.movePosition(QtGui.QTextCursor.EndOfBlock,QtGui.QTextCursor.KeepAnchor)
		yield bl,startCursor
		startCursor.clearSelection()
		startCursor.movePosition(QtGui.QTextCursor.Right)
	
	bl = startCursor.block()
	startCursor.setPosition(pos2,QtGui.QTextCursor.KeepAnchor)
	yield bl,startCursor
	
# def getBlockId(cursor):
	# return cursor.blockFormat().property(QtGui.QTextFormat.UserProperty).toPyObject()
		
	

class TSClassManager:
	"""This class will manage all the styles either the bloc of the char 
	ones."""
	def __init__(self,listBlockStyle,listCharStyle,textedit=None):
		"""
		- listBlockStyle : the list of the TSFormatClassBloc instances
		- listCharStyle : the list of the TSFormatClassChar instances
		"""
		self.listCharStyle = listCharStyle
		self.listBlockStyle = listBlockStyle
		
		
		self.dictCharStyle = {f.userPropertyId:f for f in listCharStyle} 
		self.dictBlockStyle = {f.userPropertyId:f for f in listBlockStyle} 
		self.dictStyle = {f.userPropertyId:f for f in \
										listCharStyle+listBlockStyle} 
		
		self.textedit = textedit
		
		
	def toXml(self,plaintext,document):
		"""Will return the text of the document with the XML balises for each
		style.
		"""
		newText=plaintext[:]
		place_to_mark = self.get_place_to_mark(document)
					
		# We add the XML elements in the string
		gap=0 # the gap between the old and the new newText indexing
		for pos,entry in place_to_mark:
			newText = newText[:pos+gap]+entry+newText[pos+gap:]
			gap+=len(entry)
		
		newText=unicode(newText)
		# We remove the TSConstants['SEPARATOR_MOTIF']
		for style in self.listBlockStyle: 
			if isinstance(style,TSStyleClassSeparator):
				
				newText = newText.replace(
					'<'+style.xmlMark+'>'+TSConstants['SEPARATOR_MOTIF']+\
													'</'+style.xmlMark+'>',
					'<'+style.xmlMark+'/>')
				break
		return newText
	
	def get_place_to_mark(self,document):
		"""
		Will return a list of where to put the mark in the document :
		- document: the QTextDocument on to perform the position
		[(pos1,element1),(pos2,element2),...]
		"""
		
		style_char_structure=[] # the form will be:
					# [  [style1,start_element_1,stop_element_1],
					#    [style2,start_element_2,stop_element_2],...  ]
		style_block_structure=[] # the form will be:
					# [  [style1,start_element_1,stop_element_1],
					#    [style2,start_element_2,stop_element_2],...  ]
					
		# We search the place where are the styles elements 
		
		block = document.firstBlock()
		while block.blockNumber ()  >=0 : #because if empty block, its number
													# is -1
			cursor=QtGui.QTextCursor(block)
			
			qtBlockFormat = cursor.blockFormat()
			userId = qtBlockFormat.property(QtGui.QTextFormat.UserProperty)
			userId = userId.toPyObject()
			if userId!=None and self.dictBlockStyle.has_key(userId):
				# if the style exists
				style = self.dictBlockStyle[userId]
				style_block_structure.append(
					[	style,
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
				
				if self.dictCharStyle.has_key(userId):
				# 	style = self.dictCharStyle[userId]
				# 	# if cursor.atBlockStart()
				# 		# pos = cursor.position()
				# 	# else :
				# 	#if the style corresponds
				# 	if len(style_char_structure)==0: 
				# 		#if it is the first element of the list
				# 		style_char_structure.append([style,cursor.position()-1,
				# 							  cursor.position()])
				# 	elif 	(not cursor.atBlockStart()) and \
				# 			style==style_char_structure[-1][0] and \
				# 			style_char_structure[-1][-1]==cursor.position(): 
				# 		# if we are not at the begining of a new paragraph
				# 		# and the previous char was already under the same 
				# 		# style:
				# 		style_char_structure[-1][-1]+=1
				# 		
				# 	else: #if it is a new element
				# 		style_char_structure.append([style,cursor.position(),
				# 							  cursor.position()+1])

					#if the style corresponds
					style = self.dictCharStyle[userId]
					pos = cursor.position()
					
					if 		len(style_char_structure)==0 or \
							style != style_char_structure[-1][0] or \
							pos  != style_char_structure[-1][-1]+1:
						# if it is the first element of the list or the 
						# previous char was not already under the same style:
						style_char_structure.append( [style,pos-1,pos] )
						
					else :
						# if the previous char was already under the same 
						# style:
						style_char_structure[-1][-1] += 1

				
			block = block.next()
		# We search the place where to put the XML elements in the final 
		# string:
		d = {}
		for style,start,end in style_char_structure:
			d[start] = d.get(start,'')+'<'+style.xmlMark+'>' 
			assert not d.has_key(end)
			d[end] = '</'+style.xmlMark+'>' 
		for style,start,end in style_block_structure :
			# if isinstance(style,TSFormatClassSeparator):
			# 	d[start] = '\n<'+style.xmlMark+'/>' + d.get(start,'') 
			# else : 
			d[start] = '<'+style.xmlMark+'>' + d.get(start,'') 
			d[end] =  d.get(end,'') + '</'+style.xmlMark+'>' 
		list_keys = d.keys()
		list_keys.sort()
		place_to_mark = [(i,d[i]) for i in list_keys]
		return place_to_mark
		
		
	def fromXml(self,document):
		"""Will replace the XML elements of the text in the QTextEdit in the 
		good formating """
		cursor = QtGui.QTextCursor(document)
		cursor.setPosition(document.characterCount()-1,
											QtGui.QTextCursor.KeepAnchor)
		for blocFormat in self.listBlockStyle:
			blocFormat.setIdFromXml(document)
			self.recheckBlockStyle(cursor)
		for charFormat in self.listCharStyle:
			charFormat.setIdFromXml(document)
			self.recheckCharStyle(cursor)
		

				
	def recheckCharStyle(self,cursor):
		"""
		Will recheck the char style under the cursor selection
		"""
		start = cursor.selectionStart() 
		end   = cursor.selectionEnd()
		
		if start>end:
			tmp = end
			end=start
			start=tmp
		
		cursor1 = QtGui.QTextCursor(cursor)
		cursor1.setPosition(start)
		while cursor1.position()<end:
			cursor1.movePosition(QtGui.QTextCursor.Right,
												QtGui.QTextCursor.KeepAnchor)
			
			qtCharFormat_id = getCharId(cursor1)
			qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor1)				
			if qtCharFormat_id in self.dictCharStyle.keys():
				style = self.dictCharStyle[qtCharFormat_id]
				style.setStyleToQtFormating(qtCharFormat,cursor1.document())
			cursor1.setCharFormat(qtCharFormat)
			cursor1.clearSelection()
			
	def recheckBlockStyle(self,cursor):
		for block in cursor.yieldBlockInSelection():
			print 'block : ',block
			cursor1 = QtGui.QTextCursor(block)

			qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor1)
			cursor1.movePosition(QtGui.QTextCursor.EndOfBlock,
												QtGui.QTextCursor.KeepAnchor)
			# Why not cursor1.select(QtGui.QTextCursor.BlockUnderCursor):
			# because it applies the format also at the previsous block
			cursor1.setBlockCharFormat(qtCharFormat)
			cursor1.setBlockFormat(qtBlockFormat)
			# For the color to work (for some reason) :
			qtCharFormat.setForeground(qtCharFormat.foreground()) 
			cursor1.mergeCharFormat(qtCharFormat) # merge in order to keep the id
			
	def inverseStyle(self,cursor,style_id):
		"""
		Will inverse the style on the cursor's selection according to the syle
		corresponding to style_id
		"""
		if style_id in self.dictBlockStyle.keys():
			# cursor1 = QtGui.QTextCursor(cursor)
			style = self.dictBlockStyle[style_id]
			res = style.inverseId(cursor)
			self.recheckBlockStyle(cursor)
			self.recheckCharStyle(cursor)
			
				
		elif style_id in self.dictCharStyle.keys():
			style = self.dictCharStyle[style_id]
			res = style.inverseId(cursor)
			if cursor.hasSelection():
				for block,cursor1 in yieldBlock(cursor):
					self.recheckCharStyle(cursor1)
			else :
				qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor)
				if res : # if we have to put the syle:
					style.setStyleToQtFormating(qtCharFormat,cursor.document())
				cursor.setCharFormat(qtCharFormat)
			# self.inverseCharStyle(cursor,style_id)
		else:
			raise ValueError('Format id '+str(style_id)+' unknown !')
		
#	def inverseStyle(self,cursor,style_id):
#		"""
#		Will inverse the sytle on the cursor's selection. The cursor's 
#		selection must be only on ONE block.
#		"""
#		if style_id in self.dictBlockStyle.keys():
#			for block in cursor.yieldBlockInSelection():
#				self.inverseBlockStyle(block,style_id)
#		elif style_id in self.dictCharStyle.keys():
#			self.inverseCharStyle(cursor,style_id)
#		else:
#			raise ValueError('Format id '+str(style_id)+' unknown !')
#			
#	def inverseBlockStyle(self,block,style_id):
#		cursor = QtGui.QTextCursor(block)
#		style = self.dictBlockStyle[style_id]
#		
#		
#		res = style.inverseId(cursor)
#		qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor)
#		
#		cursor1 = QtGui.QTextCursor(cursor)
#		cursor1.select(QtGui.QTextCursor.BlockUnderCursor)
#		cursor1.setBlockCharFormat(qtCharFormat)
#		cursor1.setBlockFormat(qtBlockFormat)
#		cursor1.mergeCharFormat(qtCharFormat) # merge in order to keep the id
#		self.recheckSelection(cursor1)
#		
#	def inverseCharStyle(self,cursor,style_id):
#		style = self.dictCharStyle[style_id]
#		res = style.inverseId(cursor)
#		if cursor.hasSelection():
#			for block,cursor1 in yieldBlock(cursor):
#				self.inverseCharStyleInBlock(cursor1,style,res)
#		else:
#			qtFormat = cursor.blockCharFormat()
#			if res : # if we have to put the syle:
#				style.setStyleToQtFormating(qtFormat,cursor.document())
#			cursor.setCharFormat(qtFormat)
#		# if not res:
#			# self.setCharFormatsToBlock(cursor.block())
#			
#	def inverseCharStyleInBlock(self,cursor,style,res):
#		"""
#		will inverse the char style in ONE block (the selection of cursor
#		should be restricted in one block
#		"""
#		# qtFormat = cursor.blockCharFormat()
#		qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor)
#		if res : # if we have to put the syle:
#			style.setStyleToQtFormating(qtCharFormat,cursor.document())
#		cursor.setCharFormat(qtCharFormat)
#	
	def getDefaultFormat(self,cursor=None):
		"""
		Will return the default qtBlockFormat and qtCharFormat corresponding
		to the block of the cursor.
		"""
		if  self.textedit==None:
			qtCharFormat = QtGui.QTextCharFormat()
			qtBlockFormat = QtGui.QTextBlockFormat()
		else:
			qtCharFormat = QtGui.QTextCharFormat(self.textedit.defaultCharFormat)
			qtBlockFormat = QtGui.QTextBlockFormat(self.textedit.defaultBlockFormat)		
		
		if cursor != None:
			bl_id = getBlockId(cursor)
			if bl_id in self.dictBlockStyle.keys():
				style_bl = self.dictBlockStyle[bl_id]
				style_bl.setStyleToQtFormating([qtBlockFormat,qtCharFormat],
																cursor.document())
		return qtBlockFormat,qtCharFormat
#	
#	def resetFormat(self,cursor):
#		"""Will reset all the formating of the cursor, that is to say:
#		- the char format of the selection
#		- the block format of the whole block
#		"""
#		
#		# for block,cursor1 in yieldBlock(cursor):
#			# qtCharFormat_id = getCharId(cursor1)
#			# qtBlockFormat_id = getBlockId(cursor1)
#			
#		
#		# qtCharFormat = cursor.charFormat()
#		# qtBlockFormat = cursor.blockFormat()# QtGui.QTextFormat.UserProperty)
#		
#		# qtCharFormat_id  = getCharId(cursor)
#		# qtBlockFormat_id = getBlockId(cursor)
#		# res1 = False									
#		# res2 = False									
#		# if qtCharFormat_id in self.dictCharStyle.keys():
#			# res1 = self.dictCharStyle[qtCharFormat_id].inverseFormat(cursor)
#			
#		# if qtBlockFormat_id in self.dictBlockStyle.keys():
#			# res2 = self.dictBlockStyle[qtBlockFormat_id].inverseFormat(cursor)
#		
#		# return res1,res2
			

TSManager = TSClassManager(
	listBlockStyle = [	TSStyleSeparator,TSStyleHeader1,
						TSStyleHeader2,TSStyleHeader3,TSStyleCode,
						TSStylePhantom,TSStyleImage],
	listCharStyle = [TSStyleEmphasize])
	