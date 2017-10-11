from PyQt5 import QtGui, QtCore, QtWidgets
import copy

from .TextStylesPreferences import TSPreferences
from .TextStylesList import *


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


	def toXml(self,document):
		"""Will return the text of the document with the XML balises for each
		style.
		"""
		newText = document.toPlainText()[:]
		place_to_mark = self.get_place_to_mark(document)

		# We add the XML elements in the string
		gap=0 # the gap between the old and the new newText indexing
		for pos,entry in place_to_mark:
			newText = newText[:pos+gap]+entry+newText[pos+gap:]
			gap+=len(entry)

		newText=str(newText)
		# We remove the TSPreferences['SEPARATOR_MOTIF']
		for style in self.listBlockStyle:
			if isinstance(style,TSStyleClassSeparator):

				newText = newText.replace(
					'<'+style.xmlMark+'>'+TSPreferences['SEPARATOR_MOTIF']+\
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
			# userId = userId.toPyObject()
			if userId!=None and userId in self.dictBlockStyle:
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
				# userId = userId.toPyObject()

				if userId in self.dictCharStyle:
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
			assert end not in d
			d[end] = '</'+style.xmlMark+'>'
		for style,start,end in style_block_structure :
			# if isinstance(style,TSFormatClassSeparator):
			# 	d[start] = '\n<'+style.xmlMark+'/>' + d.get(start,'')
			# else :
			d[start] = '<'+style.xmlMark+'>' + d.get(start,'')
			d[end] =  d.get(end,'') + '</'+style.xmlMark+'>'
		list_keys = list(d.keys())
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
		pv_qtCharFormat_id = getCharId(cursor1)
		style_begin_position = cursor1.position()
		while cursor1.position()<end:
			cursor1.movePosition(QtGui.QTextCursor.Right)
			qtCharFormat_id = getCharId(cursor1)
			if pv_qtCharFormat_id!=qtCharFormat_id or cursor1.position()==end \
													or cursor1.atBlockStart():
				# If we change the style
				cursor2 = QtGui.QTextCursor(cursor1.document())
				cursor2.setPosition(style_begin_position)
				style_end_position = cursor1.position()
				if  not cursor1.position()==end:
					style_end_position -= 1
				cursor2.setPosition(style_end_position,
										QtGui.QTextCursor.KeepAnchor)

				qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor2)
				if pv_qtCharFormat_id in self.dictCharStyle.keys():
					style = self.dictCharStyle[pv_qtCharFormat_id]
					style.setStyleToQtFormating(qtCharFormat,cursor2.document())
				cursor2.setCharFormat(qtCharFormat)
				pv_qtCharFormat_id = qtCharFormat_id
				style_begin_position = cursor1.position()-1

	def recheckBlockStyle(self,cursor):
		for block in cursor.yieldBlockInSelection():
			cursor1 = QtGui.QTextCursor(block)

			qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor1)
			cursor1.movePosition(QtGui.QTextCursor.EndOfBlock,
												QtGui.QTextCursor.KeepAnchor)
			# Why not cursor1.select(QtGui.QTextCursor.BlockUnderCursor):
			# because it applies the format also at the previous block
			cursor1.setBlockCharFormat(qtCharFormat)
			cursor1.setBlockFormat(qtBlockFormat)
			# For the color to work (for some reason) :
			qtCharFormat.setForeground(qtCharFormat.foreground())
			cursor1.mergeCharFormat(qtCharFormat) # merge in order to keep the id

	def inverseStyle(self,cursor,style_id):
		"""
		Will inverse the style on the cursor's selection according to the syle
		corresponding to style_id
		returns:
		- res : True if the style has been applied, False is it has been removed
		- cursor1 : the cursor1 where have taken place the modification

		Also, cursor will be moved where to correspond to the new place where
		should be the textCursor.
		"""
		if style_id in list(self.dictBlockStyle.keys()):
			# cursor1 = QtGui.QTextCursor(cursor)
			style = self.dictBlockStyle[style_id]
			res,cursor1 = style.inverseId(cursor)
			self.recheckBlockStyle(cursor1)
			for bl,cursor2 in yieldBlock(cursor1):
				cursor2.select(QtGui.QTextCursor.BlockUnderCursor)
				self.recheckCharStyle(cursor2)
			return res,cursor1


		elif style_id in list(self.dictCharStyle.keys()):
			style = self.dictCharStyle[style_id]
			res,cursor1 = style.inverseId(cursor)
			if cursor1.hasSelection():
				for block,cursor2 in yieldBlock(cursor1):
					self.recheckCharStyle(cursor2)
			else :
				qtBlockFormat,qtCharFormat = self.getDefaultFormat(cursor1)
				if res : # if we have to put the syle:
					style.setStyleToQtFormating(qtCharFormat,cursor1.document())
				cursor1.setCharFormat(qtCharFormat)
			return res,cursor1

			# self.inverseCharStyle(cursor,style_id)
		else:
			raise ValueError('Format id '+str(style_id)+' unknown !')

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
			if bl_id in list(self.dictBlockStyle.keys()):
				style_bl = self.dictBlockStyle[bl_id]
				style_bl.setStyleToQtFormating([qtBlockFormat,qtCharFormat],
																cursor.document())
		return qtBlockFormat,qtCharFormat

	def resetStyle(self,cursor):
		"""Will reset all the formating of the cursor, that is to say:
		- the char format of the selection
		- the block format of the whole block
		"""

		res1 = False
		res2 = False
		## Let's remove the style of all the selected blocks
		for block,cursor1 in yieldBlock(cursor):
			qtBlockFormat_id = getBlockId(cursor1)

			if qtBlockFormat_id in list(self.dictBlockStyle.keys()):
				self.inverseStyle(cursor1,qtBlockFormat_id)
				res2 = True

		## Let's remove then all the styles in the selection
		if cursor.hasSelection():
			cursor1 = QtGui.QTextCursor(cursor.document())
			cursor1.setPosition(cursor.selectionStart())
			cursor1.movePosition(QtGui.QTextCursor.Right)
			last_id = None
			st_pos = cursor1.position()
			while cursor1.position()<=cursor.selectionEnd():
				new_id = getCharId(cursor1)
				if new_id!=last_id:
					if last_id!=None:
						print("cursor1.position() : ",cursor1.position())
						print("st_pos : ",st_pos)
						cursor2 = QtGui.QTextCursor(cursor1.document())
						cursor2.setPosition(st_pos)
						cursor2.setPosition(cursor1.position()-1,
												QtGui.QTextCursor.KeepAnchor)
						# self.textedit.setTextCursor(cursor2)
						self.inverseStyle(cursor2,last_id)

					last_id = new_id
					st_pos = cursor1.position()-1 # it take the style of the
						# previous char
					res1=True

				cursor1.movePosition(QtGui.QTextCursor.Right)
				if cursor1.atEnd():
					break
			if last_id!=None:
				cursor2 = QtGui.QTextCursor(cursor1)
				cursor2.setPosition(st_pos, QtGui.QTextCursor.KeepAnchor)
				self.inverseStyle(cursor2,last_id)


			# if qtCharFormat_id in self.dictCharStyle.keys():
				# print "coucou1"
				# self.inverseStyle(cursor1,qtCharFormat_id)
				# res1 = True
		return res1,res2


TSManager = TSClassManager(
	listBlockStyle = [	TSStyleSeparator,TSStyleHeader1,
						TSStyleHeader2,TSStyleHeader3,TSStyleCode,
						TSStylePhantom,TSStyleImage],
	listCharStyle = [TSStyleEmphasize,TSStyleStyleColor1,TSStyleStyleColor2,TSStyleStyleColor3])
