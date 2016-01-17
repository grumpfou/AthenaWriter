"""
This file will contain gui solution to deal with the object ConstantsManager
"""
############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################

from PyQt4 import QtGui, QtCore

from CommonObjects.CommonObjects import *
from CommonObjects.CommonObjectsWidgets import COWidgetsDict

doubleSpinBoxStep = .1
class CMWidget (QtGui.QWidget):
	def __init__(self,constants_manager,constraints_dict=None,key_list=None,
				*args,**kargs):
		""" This class will manage the constants with a gui interface. Each
		value is caracterized by its name (called key), its type, its 
		initial value and its description. These information are given in 
		values_dict.
		- constants_manager : the constant manager instance to represent
		
		"""		
		QtGui.QWidget.__init__(self,*args,**kargs)
		if constraints_dict==None : constraints_dict={}
		self.constants_manager = constants_manager
		self.constraints_dict = self.constants_manager.constrains
		self.widget_dict = {}
		# if key_list==None:
			# key_list = 
		
		layout  = QtGui.QFormLayout ()
		for k in self.constants_manager.keys():
			# if widget_dict.has_key(k):
				# wid = widget_dict[k]
			# else:
				# wid = self.getCstWidget(k)
			wid = self.getCstWidget(k)
			layout.addRow(k.title(),wid)
			self.widget_dict[k] = wid
		self.setLayout(layout)
		
		
		
		
	def getCstWidget(self,key):
		"""Will give the widget correponding to a certain type of value:
		- key : the key of the value.
			will work for basic value type
		
		"""
		type_ = self.constants_manager.start_defaults[key][0]
		value = self.constants_manager[key]
		descr =  self.constants_manager.descriptions.get(key,None)
		if self.constraints_dict.has_key(key):
			constraints = self.constraints_dict[key]
		else:
			constraints = {}
			

		if COWidgetsDict.has_key(type_):
			wid = COWidgetsDict[type_](self,value,**constraints)
		else:
			for k in COWidgetsDict.keys():
				if issubclass(type_,k):
					wid = COWidgetsDict[k](self,value,**constraints)
					break	
			else :
				import textwrap
				msg = textwrap.fill(\
					'The type of the value '+key+' is not convertible into a '+\
					'widget.')
				raise CMError(msg)
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
		except CMError,m:
			QtGui.QMessageBox.critical(self,"Error of syntax",
											"For the value "+key+":\n"+str(m))
			
	
	def getValueDict(self,skip_same_as_init=False):
		"""Will return the dictionary of the values
		- skip_same_as_init : if True, will return only the one that have 
				changed since the begining.
		"""
		res = {}
		for k in self.constants_manager.keys():
			v = self.getValue(k)
			if (not skip_same_as_init) or v!=self.constants_manager[k]:
				res[k]=v
		return res
		
	
		

class CMDialog (QtGui.QDialog):
	def __init__(self,parent=None,*args,**kargs):
		QtGui.QDialog.__init__(self,parent=parent)
		# self.wid = CMWidget(parent=self,*args,**kargs)
		
		# self.wid = CMWidget(**kargs)
		self.wid = CMWidget(constants_manager = kargs['constants_manager'])
		
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
		
		dialog = CMDialog(*args,**kargs)
		result = dialog.exec_()
		d = dialog.wid.getValueDict(skip_same_as_init=skip_same_as_init)
		dialog.close()
		
		if result == QtGui.QDialog.Accepted:
			return d	
		else:
			return False		
	


		
if __name__=='__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	import ConstantsManager
	class CMM (ConstantsManager.CMConstantsManager):
		start_defaults 			= { 
				"K_int" :(int,153									),
				"K_flo" :(float,153.5								),
				"K_uni" :(unicode,"tote"							),
				"K_boo" :(bool,False								),
				"K_lis" :(list,["tote","toti"]						),
				"K_dic" :(dict,{"tote":"tote__","toti":"toti__"}	),
				# "K_dicC":(COContrainedDict,{"tote":None,"toti":None}),
				}
				
	c = CMWidget(CMM())
	c.show()
	sys.exit(app.exec_())
	# class COChoice1 (COChoice):
	# 	elements_list= ['tata','toto','titi']
	# 	
	# 	
	# constraints_dict = {
	# 		"K_int" : [0,1000],
	# 		}
	# 		
	# 	descriptions ={
	# 			"K_int" :"Desc_int"	,
	# 			"K_flo" :"Desc_flo"	,
	# 			"K_uni" :"Desc_uni"	,
	# 			"K_boo" :"Desc_boo"	,
	# 			"K_lis" :"Desc_lis"	,
	# 			"K_dic" :"Desc_dic"	,
	# 			# "K_dicC":"Desc_dicC",
	# 			"K_cho" :"Desc_cho"	,
	# 			}
	# 		
	# 		
	# 
	# d = CMWidget(constants_manager=CMM())
	# # d = QtGui.QTextEdit(parent=None)
	# d.show()
	# sys.exit(app.exec_())
	# # dv = CMDialog.getValueDict(parent=None,values_dict=values_dict,
											# constraints_dict=constraints_dict)

	# dv.close()
	# dv.show()
	# butt = QtGui.QPushButton()
	# app.connect(butt,QtCore.SIGNAL('clicked()'), dv.getValueDict)
	# butt.show()
	# print "coucou"
	# print "toto"
