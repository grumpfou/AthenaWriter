from PyQt4 import QtGui, QtCore
from DialogValuesAdditionalTypes import *

class DVWidgetBool(QtGui.QCheckBox):
	def __init__(self,parent,value=True):
		QtGui.QCheckBox.__init__(self,parent=parent)

		if value:
			self.setCheckState(QtCore.Qt.Checked)
		else:
			self.setCheckState(QtCore.Qt.Unchecked)
			
	def getValue(self):
		if self.checkState () == QtCore.Qt.Checked:
			return True
		else :
			return False



class DVWidgetInt(QtGui.QSpinBox):
	def __init__(self,parent,value=0,minimum=0,maximum=100,step=1):
		QtGui.QSpinBox.__init__(self,parent=parent)
		self.setMinimum ( minimum )
		self.setMaximum ( maximum )
		self.setSingleStep ( step )
		self.setValue(value)
		
	def getValue(self):
		return int(self.value())
		
class DVWidgetFloat(QtGui.QDoubleSpinBox):
	def __init__(self,parent,value=0,minimum=0,maximum=100,step=.1):
		QtGui.QDoubleSpinBox.__init__(self,parent=parent)
		self.setMinimum ( minimum )
		self.setMaximum ( maximum )
		self.setSingleStep ( step )
		self.setValue(value)
		
	def getValue(self):
		return float(self.value())
		
					
class DVWidgetUnicode(QtGui.QLineEdit):
	def __init__(self,parent,value=None):
		if value==None: value=""
		QtGui.QLineEdit.__init__(self,parent=parent)
		self.setText(value)
		
	def getValue(self):
		return unicode(self.text())
		
class DVWidgetList(QtGui.QLineEdit):
	additional_descr = 'Separate different values by comma'
	def __init__(self,parent,value=None):
		"""
		Widget that will represent the lists
		"""
		QtGui.QLineEdit.__init__(self,parent=parent)
		if value==None: value=[]
		self.setList(value)
	
	def setList(self,a):
		a = ','.join(a)
		self.setText(a)
		
	def getValue(self):
		res = self.text()
		res = res.split(',')
		return res
		
class DVWidgetDict(QtGui.QLineEdit):
	additional_descr='Use the syntax "Key1:Value1,Key2:value2" etc.'
	def __init__(self,parent,value=None):
		"""
		Widget that will represent the dict
		"""
		QtGui.QLineEdit.__init__(self,parent=parent)
		if value==None: value={}
		self.setDict(value)
	
	
	def setDict(self,d):
		a = ' , '.join([' : '.join([k,str(v)]) for k,v in d.items()])
		self.setText(a)
		
	def getValue(self):
		text = self.text()
		l = text.split(',')
		res ={}
		for a in l:
			keyvalue = a.split(':')
			if len(keyvalue)==1:
				raise DVError('Wrong syntax for the dictionary, use '+\
					'the syntax "Key1:Value1,Key2:value2" etc.')
			v = ':'.join([unicode(i) for i in keyvalue[1:]]).strip()
			res[unicode(keyvalue[0]).strip()] = v
		return res
		
class DVWidgetContrainedDict(DVWidgetDict):
	def __init__(self,parent,values):
		"""
		Widget that will represent the DVContrainedDict
		"""
		DVWidgetDict.__init__(self,parent,values)
		self.constrainedDictKeys = values.keys()
		
	def setDict(self,d):
		DVWidgetDict.setDict(self,d)
		self.constrainedDictKeys = d.keys()
	
	def getValue(self):
		res0 = DVWidgetDict.getValue(self)
		res1 = DVContrainedDict(self.constrainedDictKeys)
		res1.update(res0)
		return res1
		
class DVWidgetChoice(QtGui.QComboBox):
	"""
	Widget that will represent the DVChoice
	"""
	def __init__(self,values):
		self.choice = values
		QtGui.QComboBox.__init__ ( self )
		# print 'self.choice.elements_list : ',self.choice.elements_list
		li = [unicode(l) for l in self.choice.elements_list]
		self.addItems(li)
		
		i = self.choice.elements_list.index(self.choice.active_element)
		QtGui.QComboBox.setCurrentIndex ( self , i )
	
	def getValue(self):
		a = unicode(self.currentText())
		
		c = self.choice.copy()
		c.set_active_element(a,fromString=True)
		return c
		
		
DVWidgets = {
	bool : DVWidgetBool,
	int : DVWidgetInt,
	float : DVWidgetFloat,
	unicode: DVWidgetUnicode,
	list: DVWidgetList,
	dict: DVWidgetDict,
	DVContrainedDict: DVWidgetContrainedDict,
	DVChoice:DVWidgetChoice,
	}

