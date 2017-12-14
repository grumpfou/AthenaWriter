from PyQt5 import QtGui, QtCore, QtWidgets
from .CommonObjects import *
from FileManagement.FileManagement import FMTextFileManagement
from pathlib import Path

class COWidgetBool(QtWidgets.QCheckBox):
	def __init__(self,parent=None,value=True):
		QtWidgets.QCheckBox.__init__(self,parent=parent)

		if value:
			self.setCheckState(QtCore.Qt.Checked)
		else:
			self.setCheckState(QtCore.Qt.Unchecked)

	def getValue(self):
		if self.checkState () == QtCore.Qt.Checked:
			return True
		else :
			return False



class COWidgetInt(QtWidgets.QSpinBox):
	def __init__(self,parent,value=0,min=0,max=1e9,step=1):
		QtWidgets.QSpinBox.__init__(self,parent=parent)
		self.setMinimum ( min )
		self.setMaximum ( max )
		self.setSingleStep ( step )
		self.setValue(value)

	def getValue(self):
		return int(self.value())

class COWidgetFloat(QtWidgets.QDoubleSpinBox):
	def __init__(self,parent,value=0,min=0,max=100,step=.1):
		QtWidgets.QDoubleSpinBox.__init__(self,parent=parent)
		self.setMinimum ( min )
		self.setMaximum ( max )
		self.setSingleStep ( step )
		self.setValue(value)

	def getValue(self):
		return float(self.value())


class COWidgetUnicode(QtWidgets.QLineEdit):
	def __init__(self,parent,value=None):
		if value==None: value=""
		QtWidgets.QLineEdit.__init__(self,parent=parent)
		self.setText(value)

	def getValue(self):
		return str(self.text())

class COWidgetList(QtWidgets.QLineEdit):
	additional_descr = 'Separate different values by comma'
	def __init__(self,parent,value=None):
		"""
		Widget that will represent the lists
		"""
		QtWidgets.QLineEdit.__init__(self,parent=parent)
		if value==None: value=[]
		self.setList(value)

	def setList(self,a):
		a = ','.join(a)
		self.setText(a)

	def getValue(self):
		res = self.text()
		res = res.split(',')
		return res

class COWidgetDict(QtWidgets.QLineEdit):
	additional_descr='Use the syntax "Key1:Value1,Key2:value2" etc.'
	def __init__(self,parent,value=None):
		"""
		Widget that will represent the dict
		"""
		QtWidgets.QLineEdit.__init__(self,parent=parent)
		if value==None: value={}
		self.setDict(value)


	def setDict(self,d):
		a = ' , '.join([' : '.join([k,str(v)]) for k,v in list(d.items())])
		self.setText(a)

	def getValue(self):
		text = self.text()
		l = text.split(',')
		res ={}
		for a in l:
			keyvalue = a.split(':')
			if len(keyvalue)==1:
				raise COError('Wrong syntax for the dictionary, use '+\
					'the syntax "Key1:Value1,Key2:value2" etc.')
			v = ':'.join([str(i) for i in keyvalue[1:]]).strip()
			res[str(keyvalue[0]).strip()] = v
		return res

class COWidgetContrainedDict(COWidgetDict):
	def __init__(self,parent,values):
		"""
		Widget that will represent the COContrainedDict
		"""
		COWidgetDict.__init__(self,parent,values)
		self.constrainedDict = values

	def setDict(self,d):
		COWidgetDict.setDict(self,d)
		self.constrainedDict = d

	def getValue(self):
		res0 = COWidgetDict.getValue(self)
		res1 = self.constrainedDict
		res1.update(res0)
		return res1

class COWidgetChoice(QtWidgets.QComboBox):
	"""
	Widget that will represent the COChoice
	"""
	def __init__(self,parent,values):
		self.choice = values
		QtWidgets.QComboBox.__init__ ( self ,parent=parent)
		# print 'self.choice.elements_list : ',self.choice.elements_list
		li = [str(l) for l in self.choice.elements_list]
		self.addItems(li)

		i = self.choice.elements_list.index(self.choice.active_element)
		QtWidgets.QComboBox.setCurrentIndex ( self , i )

	def getValue(self):
		a = str(self.currentText())

		c = self.choice.copy()
		c.set_active_element(a,fromString=True)
		return c

class COWidgetPath(QtWidgets.QWidget):
	"""
	Widget that will represent the Path (from pathlib)
	"""
	def __init__(self,parent,init_path='.',**kargs_browse):
		""" kargs_browse: to pass when openning the QFileDialog
		"""

		QtWidgets.QWidget.__init__ ( self ,parent=parent)
		self.lineEdit = QtWidgets.QLineEdit(str(init_path),parent=self)
		self.button = QtWidgets.QPushButton("➚")
		width = self.button.fontMetrics().boundingRect("➚").width() + 7
		self.button.setMaximumWidth(width)
		hlayout = QtWidgets.QHBoxLayout()
		hlayout.addWidget(self.lineEdit)
		hlayout.addWidget(self.button)
		self.setLayout(hlayout)
		self.kargs_browse = kargs_browse
		self.button.clicked.connect(self.browse)

	def browse(self):
		filepath = FMTextFileManagement.open_gui_filepath(
			dft_opening_saving_site= self.lineEdit.text(),
			**self.kargs_browse)
		if filepath:
			self.lineEdit.setText(filepath)

	def getValue(self):
		return Path(self.lineEdit.text())


COWidgetsDict = {
	bool : COWidgetBool,
	int : COWidgetInt,
	float : COWidgetFloat,
	str: COWidgetUnicode,
	str: COWidgetUnicode,
	list: COWidgetList,
	dict: COWidgetDict,
	COContrainedDict: COWidgetContrainedDict,
	COChoice:COWidgetChoice,
	Path: COWidgetPath,
	}
