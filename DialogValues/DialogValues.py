"""
This class will be usefull in many part of the program. From a list of values,

It creates a widget and a dialog where every information in entry can be 
changed according to its type (if it is a int, you will have a QSpinBox ect.
"""
from PyQt4 import QtGui, QtCore
from DialogValuesWidget import DVWidgets
from DialogValuesAdditionalTypes import *




doubleSpinBoxStep = .1
class DVWidget (QtGui.QWidget):
	def __init__(self,values_dict,widget_dict=None,key_list=None,
			constraints_dict=None,*args,**kargs):
		""" This class will manage the constants with a gui interface. Each
		value is caracterized by its name (called key), its type, its 
		initial value and its description. These information are given in 
		values_dict.
		
		- values_dict under the form:
			{key : ( type, current_value ,decr) ,...}
		- widget_dict under the form:
			{key :  widget_to_display,...}
			any widget should contain the method getValue in order to extract
			the information
		- key_list : list of key in the order to be displayed
		- constraints : for each type its constraint
			int : (min,max,interval)
			float : (min,max,interval)
			
			Should be under the form:
			{key :  (constraints1, constraints2, ...) ,...}
		
		"""
		QtGui.QWidget.__init__(self,*args,**kargs)
		
		if key_list == None : key_list =[]
		if widget_dict == None : widget_dict ={}
		if constraints_dict == None : constraints_dict ={}
		
		self.keys = key_list[:]

		self.values_dict = values_dict
		self.constraints_dict = constraints_dict
		self.widget_dict = {}
		self.initial_dict = {k : v[1] for k,v in self.values_dict.items()}
		
		keys_of_constants_dict = self.values_dict.keys()
		for k in self.keys:
			try :
				keys_of_constants_dict.pop(keys_of_constants_dict.index(k))
			except ValueError:
				raise ValueError('The key '+k+' of key_list should be a key '+\
						'of contants_dict')
		keys_of_constants_dict.sort()
		self.keys += keys_of_constants_dict
		layout  = QtGui.QFormLayout ()
		for k in self.keys:
			if widget_dict.has_key(k):
				wid = widget_dict[k]
			else:
				wid = self.getCstWidget(k)
			layout.addRow(k.title(),wid)
			self.widget_dict[k] = wid
		self.setLayout(layout)
		
	
	def getCstWidget(self,key):
		"""Will give the widget correponding to a certain type of value:
		- key : the key of the value.
			will work for basic value type
		
		"""
		type_ = self.values_dict[key][0]
		value = self.values_dict[key][1]
		descr = self.values_dict[key][2]
		if self.constraints_dict.has_key(key):
			constraints = self.constraints_dict[key]
		else:
			constraints = []
			

		if DVWidgets.has_key(type_):
			wid = DVWidgets[type_](self,value,*constraints)
		else:
			for k in DVWidgets.keys():
				if issubclass(type_,k):
					
					wid = DVWidgets[k](value,*constraints)
					break
			else :
				import textwrap
				msg = textwrap.fill(\
					'The type of the value '+key+' is not convertible into a '+\
					'widget.')
				raise DVError(msg)
		if wid.__dict__.has_key('additional_descr'):
			descr += '\n' + wid.additional_descr
		if descr!=None:
			wid.setToolTip(descr)
		return wid
			
		
	def getValue(self,key):
		"""Will return the value of the value of the correponding key"""
		try:
			wid = self.widget_dict[key]
			return wid.getValue()
		except DVError,m:
			QtGui.QMessageBox.critical(self,"Error of syntax",
											"For the value "+key+":\n"+str(m))
			
	
	def getValueDict(self,skip_same_as_init=False):
		"""Will return the dictionary of the values
		- skip_same_as_init : if True, will return only the one that have 
				changed since the begining.
		"""
		res = {}
		for k in self.keys:
			v = self.getValue(k)
			if (not skip_same_as_init) or v!=self.initial_dict[k]:
				res[k]=v
		return res
		

class DVDialog (QtGui.QDialog):
	def __init__(self,parent=None,*args,**kargs):
		QtGui.QDialog.__init__(self,parent=parent)
		self.wid = DVWidget(*args,**kargs)
		
		button_ok = QtGui.QPushButton("&OK")
		button_cancel = QtGui.QPushButton("&Cancel")
		
		layout_button =  QtGui.QHBoxLayout()
		layout_button.addWidget( button_ok )
		layout_button.addWidget( button_cancel )
		
		self.main_layout = QtGui.QVBoxLayout()
		self.main_layout.addWidget(self.wid)
		
		self.main_layout.addLayout(layout_button)
		self.setLayout ( self.main_layout )
		

		# Connections:
		self.connect(button_ok,QtCore.SIGNAL("clicked()"),self.accept)
		self.connect(button_cancel,QtCore.SIGNAL("clicked()"),self.reject)
		
	@staticmethod
	def getValueDict(*args,**kargs):
		if kargs.has_key('skip_same_as_init'):
			skip_same_as_init = kargs.pop('skip_same_as_init')
		else:
			skip_same_as_init = False
		
		dialog = DVDialog(*args,**kargs)
		result = dialog.exec_()
		d = dialog.wid.getValueDict(skip_same_as_init=skip_same_as_init)
		dialog.close()
		
		if result == QtGui.QDialog.Accepted:
			return d	
		else:
			return False		
	


		
if __name__=='__main__':
	import sys
	class DVChoice1 (DVChoice):
		elements_list= ['tata','toto','titi']
	constraints_dict = {
			"K_int" : [0,1000],
			}
	values_dict	=	{
			"K_int" :(int,153,"Desc_int"),
			"K_flo" :(float,153.5,"Desc_flo"),
			"K_uni" :(unicode,"tote","Desc_uni"),
			"K_boo" :(bool,False,"Desc_boo"),
			"K_lis" :(list,["tote","toti"],"Desc_lis"),
			"K_dic" :(dict,{"tote":"tote__","toti":"toti__"},"Desc_dic"),
			"K_dicC":(DVContrainedDict,{"tote":None,"toti":None},"Desc_dicC"),
			"K_cho" :(DVChoice1,DVChoice1("toto"),"Desc_cho"),
			}
	
	app = QtGui.QApplication(sys.argv)
	
	dv = DVDialog.getValueDict(parent=None,values_dict=values_dict,
											constraints_dict=constraints_dict)
	if dv:
		print 'dv : ',dv
	# dv.close()
	# dv.show()
	# butt = QtGui.QPushButton()
	# app.connect(butt,QtCore.SIGNAL('clicked()'), dv.getValueDict)
	# butt.show()
	print "coucou"
	sys.exit(app.quit())
	print "toto"
	