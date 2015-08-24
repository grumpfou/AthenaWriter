from PyQt4 import QtGui, QtCore
import copy

# DEBUG TO CHANGE !!!!
import sys,os
d,f = os.path.split(__file__)
d = os.path.join(d,'..')
sys.path.append(os.path.abspath(d))
from DialogValues.DialogValues import DVWidget
from ConfigLoading.ConfigLoading import CLPreferences

class CMDialog (QtGui.QDialog):
	def __init__(self,constants, file_manager=None,main_constants_name=None,
																*args,**kargs):
		"""
				- file_manager : FMFileConstants instance
		"""
		QtGui.QDialog.__init__(self,*args,**kargs)
		self.constants 		= constants
		self.file_manager 	= file_manager
		if main_constants_name==None : main_constants_name='General'
		
		button_ok 		= QtGui.QPushButton('Save')
		button_cancel	= QtGui.QPushButton('Cancel')
		
		tab_widget = QtGui.QTabWidget()
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(tab_widget)
		mainLayout.addWidget(button_ok)
		mainLayout.addWidget(button_cancel)
		
		
		self.setLayout(mainLayout)
		constants = [self.constants]+\
							[v for v in self.constants.sub_constants.values()]
		self.constants_names = [ main_constants_name ] + \
							[k for k in self.constants.sub_constants.keys()]
		self.wid_list = []
		for c,m in zip(constants,self.constants_names):
			values_dict = {}
			for k,v in c.all_constants.items():
				values_dict [k] = (v[0], c.constants[k],v[2])
			w = DVWidget(values_dict =values_dict)
			tab_widget.addTab(w,m)
			self.wid_list.append(w)
			
		self.connect(	button_ok, 
						QtCore.SIGNAL('clicked()'), 
						self.SLOT_replace_constants)
		self.connect(	button_cancel, 
						QtCore.SIGNAL('clicked()'), 
						self.close)
			
	def SLOT_replace_constants(self):
		new_dict = self.wid_list[0].getValueDict(skip_same_as_init=True)
		
		for w,k in zip(self.wid_list[1:],self.constants_names[1:]):
			d = w.getValueDict(skip_same_as_init=True)
			new_dict.update({k+'.'+kk:vv for kk,vv in d.items()})
		print 'new_dict : ',new_dict
		for k,v in new_dict.items():
			self.constants[k] = v
			
		CLPreferences.replace(self.constants.to_string(skip_same_as_dft=True))
		self.close()
		
			
		# def
# 		self.new_constants = copy.deepcopy(constants)
# 		self.dictionnary = self.constants.to_dict()
# 		QtGui.QDialog.__init__(self,*args,**kargs)
# 		
# 		
# 		self.table = QtGui.QTableWidget(len(self.dictionnary.keys()), 
# 															2, parent =self)
# 		# creating the key list of the constants:
# 		self.keys_list = self.dictionnary.keys()
# 		KK_const = []
# 		KK_subco = []
# 		for i,v in enumerate(self.keys_list):
# 			if '.' in v: #if it is a sub-constant key
# 				KK_subco.append(v)
# 			else:
# 				KK_const.append(v)
# 		self.keys_list = sorted(KK_const)+sorted(KK_subco)
# 		
# 		# Put the constants keys and values in the table :
# 		self.setConstants()
# 
# 		self.table.verticalHeader().setVisible(False)   # remove the headers	
# 		self.table.horizontalHeader().setVisible(False) # remove the headers
# 		
# 		main_layout=QtGui.QVBoxLayout()
# 		main_layout.addWidget(self.table)
# 		main_layout.addWidget(button_ok	)
# 		main_layout.addWidget(button_cancel)
# 		
# 		self.connect(	button_ok, 
# 						QtCore.SIGNAL('clicked()'), 
# 						self.SLOT_replace_constants)
# 		self.connect(	button_cancel, 
# 						QtCore.SIGNAL('clicked()'), 
# 						QtCore.SLOT("close()"))
# 		self.connect(	self.table,
# 						QtCore.SIGNAL('cellChanged(int, int)'), 
# 						self.SLOT_changeVariable)
# 		self.setLayout(main_layout)
# 		
# 		self.to_change = {}
# 	
# 	
# 	def setConstants(self):
# 		for i,k in enumerate(self.keys_list):
# 			x = self.dictionnary[k]
# 			key_item = QtGui.QTableWidgetItem(k)
# 			opt_item = QtGui.QTableWidgetItem(str(x[0]))
# 			key_item.setFlags(QtCore.Qt.ItemIsSelectable)
# 			key_item.setToolTip(x[3])
# 			opt_item.setToolTip(x[3])
# 			self.table.setItem(i,0,key_item)	
# 			self.table.setItem(i,1,opt_item)	
# 		self.table.resizeColumnsToContents()
# 	
# 	def show(self):
# 		w = self.table.horizontalHeader().length()
# 		QtGui.QDialog.show(self)
# 		size = self.size()
# 		size.setWidth (w)
# 		self.resize(size)
# 	
# 	################### SLOTS ################### 
# 	def SLOT_changeVariable(self,row,column):
# 		key = self.keys_list[row]
# 		item = self.table.item(row,column)
# 		new_value = item.text()
# 		try:
# 			self.new_constants[key] = new_value
# 		except ValueError:
# 			mess = "Can not convert '"+new_value+"' into a "+\
# 					unicode(self.constants.all_constants[key][0])
# 			
# 			msgBox=QtGui.QMessageBox.critical(self,"Convert Error", mess)
# 			item.setText(unicode(self.new_constants[key]))
# 		else:
# 			self.to_change[key] = new_value
# 			
# 	def SLOT_replace_constants(self):
# 		for k,v in self.to_change.items():
# 			self.constants[k]=v
# 		if len(self.to_change)>0:
# 			mess = "You may need to have to restart the program to see the "+\
# 					"changes."
# 			QtGui.QMessageBox.information(self,"Restart?",mess)
# 			self.constants.saveFile(file_manager=self.file_manager)
# 		self.close()
# 	#############################################

		
if __name__ == '__main__':
	import sys
	
	sys.path.append('..')
	try:
		from AthenaWriterConstants import *
	except IOError:
		pass
	
	app = QtGui.QApplication(sys.argv)
	writerText = CMDialog(constants=AWConstants,parent=None)
	writerText.show()
	# print 'self.dictionnary : ',writerText.dictionnary.keys()

	sys.exit(app.exec_())
	
			