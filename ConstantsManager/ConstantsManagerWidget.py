"""
This file will contain gui solution to deal with the object ConstantsManager
"""
############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################

from PyQt5 import QtGui, QtCore, QtWidgets

from CommonObjects.CommonObjects import *
from CommonObjects.CommonObjectsWidgets import COWidgetsDict
from pathlib import Path

doubleSpinBoxStep = .1
class CMWidget (QtWidgets.QWidget):
	def __init__(self,constants_manager,constraints_dict=None,key_list=None,
				*args,**kargs):
		""" This class will manage the constants with a gui interface. Each
		value is caracterized by its name (called key), its type, its
		initial value and its description. These information are given in
		values_dict.
		- constants_manager : the constant manager instance to represent

		"""
		QtWidgets.QWidget.__init__(self,*args,**kargs)
		if constraints_dict==None : constraints_dict={}
		self.constants_manager = constants_manager
		self.constraints_dict = self.constants_manager.constrains
		self.widget_dict = {}
		# if key_list==None:
			# key_list =

		layout  = QtWidgets.QFormLayout ()
		for k in list(self.constants_manager.keys()):
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
		if key in self.constraints_dict:
			constraints = self.constraints_dict[key]
		else:
			constraints = {}


		if type_ in COWidgetsDict:
			wid = COWidgetsDict[type_](self,value,**constraints)
		else:
			for k in list(COWidgetsDict.keys()):
				if issubclass(type_,k):
					wid = COWidgetsDict[k](self,value,**constraints)
					break
			else :
				import textwrap
				msg = textwrap.fill(\
					'The type of the value '+key+' is not convertible into a '+\
					'widget.')
				raise CMError(msg)
		if 'additional_descr' in wid.__dict__:
			descr += '\n' + wid.additional_descr
		if descr!=None:
			wid.setToolTip(descr)
		return wid

	def getValue(self,key):
		"""Will return the value of the value of the correponding key"""
		try:
			wid = self.widget_dict[key]
			return wid.getValue()
		except CMError as m:
			QtWidgets.QMessageBox.critical(self,"Error of syntax",
											"For the value "+key+":\n"+str(m))


	def getValueDict(self,skip_same_as_init=False):
		"""Will return the dictionary of the values
		- skip_same_as_init : if True, will return only the one that have
				changed since the begining.
		"""
		res = {}
		for k in list(self.constants_manager.keys()):
			v = self.getValue(k)
			if (not skip_same_as_init) or v!=self.constants_manager[k]:
				res[k]=v
		return res




class CMDialog (QtWidgets.QDialog):
	def __init__(self,parent=None,*args,**kargs):
		QtWidgets.QDialog.__init__(self,parent=parent)
		# self.wid = CMWidget(parent=self,*args,**kargs)

		# self.wid = CMWidget(**kargs)
		self.wid = CMWidget(constants_manager = kargs['constants_manager'])

		button_ok = QtWidgets.QPushButton("&OK")
		button_cancel = QtWidgets.QPushButton("&Cancel")

		layout_button =  QtWidgets.QHBoxLayout()
		layout_button.addWidget( button_ok )
		layout_button.addWidget( button_cancel )

		self.main_layout = QtWidgets.QVBoxLayout()
		self.main_layout.addWidget(self.wid)

		self.main_layout.addLayout(layout_button)
		self.setLayout ( self.main_layout )


		# Connections:
		button_ok.clicked.connect(self.accept)
		button_cancel.clicked.connect(self.reject)

	@staticmethod
	def getValueDict(*args,**kargs):
		if 'skip_same_as_init' in kargs:
			skip_same_as_init = kargs.pop('skip_same_as_init')
		else:
			skip_same_as_init = False

		dialog = CMDialog(*args,**kargs)
		result = dialog.exec_()
		d = dialog.wid.getValueDict(skip_same_as_init=skip_same_as_init)
		dialog.close()

		if result == QtWidgets.QDialog.Accepted:
			return d
		else:
			return False




if __name__=='__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	import ConstantsManager
	class CMM (ConstantsManager.CMConstantsManager):
		start_defaults 			= {
				"K_int" :(int,153									),
				"K_flo" :(float,153.5								),
				"K_uni" :(str,"tote"							),
				"K_boo" :(bool,False								),
				"K_lis" :(list,["tote","toti"]						),
				"K_dic" :(dict,{"tote":"tote__","toti":"toti__"}	),
				"K_pat" :(Path,'~'	),
				# "K_dicC":(COContrainedDict,{"tote":None,"toti":None}),
				}

	c = CMWidget(CMM())
	c.show()
	sys.exit(app.exec_())
