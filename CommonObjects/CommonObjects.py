from PyQt5 import QtGui, QtCore, QtWidgets
############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################

from TextEdit.TextEditPreferences import TEDictCharReplace


class COError (Exception):pass

class COContrainedDict(dict):
	list_keys = []
	def __init__(self,a=None):
		"""
		If a is a list of string: it will be the keys and all the values will
		be initiated to None
		"""
		dict.__init__(self)
		if a ==None: a={}
		for k,v in list(a.items()):
			self.__setitem__(k,v)

	def __setitem__(self,k,v,protected=True):
		if protected and k not in self.list_keys:
			raise KeyError('The key '+k+' is unkown for this ContrainedDict.')
		return dict.__setitem__(self,k,v)
	def __getitem__(self,k,protected=True):
		if protected and k not in self.list_keys:
			raise KeyError('The key '+k+' is unkown for this ContrainedDict.')
		return dict.__getitem__(self,k)

## REPLACED by collections.OrdedDict
# class COOrderedDict(dict):
# 	"""
# 	A dictionnary where the order in which we putted the items is remembered
# 	and displayed again in the same order
# 	"""
# 	def __init__(self,a=None):
# 		if a!=None:
# 			if type(a)==dict:
# 				self.list_keys = list(a.keys())
# 			elif type(a)==list:
# 				self.list_keys = [v[0] for v in a]
# 			dict.__init__(self,a)
# 		else:
# 			self.list_keys = []
# 			dict.__init__(self)
#
# 	def keys(self):
# 		return self.list_keys
#
# 	def items(self):
# 		for k in list(self.keys()):
# 			yield k,self[k]
#
# 	def __setitem__(self,k,v):
# 		if k not in list(self.keys()):
# 			self.list_keys.append(k)
# 		dict.__setitem__(self,k,v)
#
# 	def pop(self,k):
# 		res = dict.pop(self,k)
# 		self.list_keys.remove(k)
# 		return res



class COChoice(list):
	def __init__(self,*args,active_element=None,**kargs):
		"""
		A simple class where we have to chose an element in a given list.

		- *args,**kargs : the element list in which the choice has to be made
		- active_element: the initial value. If None, we take the first element of the
			list
		"""
		list.__init__(self,*args,**kargs)
		if active_element==None:
			self.set_active_element(self[0])
		else:
			self.set_active_element(active_element)


	def set_active_element(self,active_element,fromString=False):
		"""
		- fromString : if true, will look if the key corresponds to the string
		version of each elements (usefull if None, is an element of the choice
		in which case, the string 'None' will return the good value).
		"""
		if fromString:
			dd = {str(k):k for k in self}
			if active_element not in list(dd.keys()):
				raise ValueError('the value `%s` is not in the elements list'%active_element)
			self.active_element = dd[active_element]
		else:
			if active_element not in self:
				raise ValueError('the value `%s` is not in the elements list'%active_element)
			self.active_element = active_element

	def __repr__(self):
		return "'%s' of %s"%(self.active_element,list.__repr__(self))

	def __str__(self):
		return str(self.active_element)

	def __hash__(self):
		return self.active_element.__hash__()


	def __eq__(self,other):
		if isinstance(other,self.__class__):
			other = other.active_element
		return self.active_element==other

	def __ne__(self,other):
		return not (self.__eq__(other))

	def copy(self,active_element=None):
		if active_element==self: return self.copy()
		if active_element==None: return self.__class__(self,active_element=self.active_element)
		else: return self.__class__(self,active_element=active_element)


class COTextCursorFunctions:
	@staticmethod
	def insertText(cursor,text):
		for k,v in TEDictCharReplace.items():
			text = text.replace(k,v)
		cursor.insertText(text)

	@staticmethod
	def lastChar(cursor,n=1):
		"""Return the left char at the distance n from the cursor (n=1 means
		the one just on the left)."""
		if cursor.atBlockStart():
			return '\n'
		else :
			cur_tmp=QtGui.QTextCursor(cursor)
			cur_tmp.clearSelection()
			for i in range(n-1):
				cur_tmp.movePosition(QtGui.QTextCursor.Left,
												QtGui.QTextCursor.MoveAnchor)
				if cur_tmp.atBlockStart():
					return '\n'
			cur_tmp.movePosition (QtGui.QTextCursor.Left,
												QtGui.QTextCursor.KeepAnchor)
			text = cur_tmp.selectedText ()
			for k,v in TEDictCharReplace.items():
				text = text.replace(v,k)
			return text

	@staticmethod
	def nextChar(cursor,n=1):
		"""Return the right char at the distance n from the cursor (n=1 means
		the one just on the right)."""
		if cursor.atBlockEnd():
			return '\n'
		else :
			cur_tmp=QtGui.QTextCursor(cursor)
			cur_tmp.clearSelection()
			for i in range(n-1):
				cur_tmp.movePosition(QtGui.QTextCursor.Right,
												QtGui.QTextCursor.MoveAnchor)
				if cur_tmp.atBlockEnd():
					return '\n'
			cur_tmp.movePosition (QtGui.QTextCursor.Right,
											QtGui.QTextCursor.KeepAnchor,n=n)
			text = cur_tmp.selectedText ()
			for k,v in TEDictCharReplace.items():
				text = text.replace(v,k)
			return text

	@classmethod
	def lastNextChar(cls,cursor):
		return cls.lastChar(cursor),cls.nextChar(cursor)


	@staticmethod
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
