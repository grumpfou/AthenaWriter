from PyQt4 import QtGui, QtCore
import copy

# DEBUG TO CHANGE !!!!
import sys,os
d,f = os.path.split(__file__)
d = os.path.join(d,'..')
sys.path.append(os.path.abspath(d))
from ConstantsManager.ConstantsManagerWidget import CMWidget
from ConfigLoadingPreferencesManagement import CLPreferencesManagement

	

class CLPreferencesDialog (QtGui.QDialog):
	def __init__(self,dict_preference, file_manager=None, *args,**kargs):
		"""
				- file_manager : FMFileConstants instance
		"""
		QtGui.QDialog.__init__(self,*args,**kargs)
		self.dict_preference 		= dict_preference
		self.file_manager 	= file_manager
		
		
		button_ok 		= QtGui.QPushButton('Save')
		button_cancel	= QtGui.QPushButton('Cancel')
		
		tab_widget = QtGui.QTabWidget()
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(tab_widget)
		mainLayout.addWidget(button_ok)
		mainLayout.addWidget(button_cancel)
		
		
		self.setLayout(mainLayout)
		
			constants = 
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
		self.new_dict=None
			
		self.connect(	button_ok, 
						QtCore.SIGNAL('clicked()'), 
						self.SLOT_replace_constants)
		self.connect(	button_cancel, 
						QtCore.SIGNAL('clicked()'), 
						self.close)
			
	def SLOT_replace_constants(self):
		self.new_dict = self.wid_list[0].getValueDict(skip_same_as_init=True)
		
		for w,k in zip(self.wid_list[1:],self.constants_names[1:]):
			d = w.getValueDict(skip_same_as_init=True)
			self.new_dict.update({k+'.'+kk:vv for kk,vv in d.items()})
		for k,v in self.new_dict.items():
			self.constants[k] = v
			
		CLPreferencesManagement.replace(self.constants.to_string(skip_same_as_dft=True))
		self.accept()
		
	@staticmethod
	def getValueDict(*args,**kargs):
		dialog = CLPreferencesDialog(*args,**kargs)
		result = dialog.exec_()
		d = dialog.new_dict
		
		if result == QtGui.QDialog.Accepted:
			assert d!=None
			return d
		else:
			return False
			

		
if __name__ == '__main__':
	import sys
	
	sys.path.append('..')
	try:
		from AthenaWriterConstants import *
	except IOError:
		pass
	
	app = QtGui.QApplication(sys.argv)
	writerText = CLPreferencesDialog(constants=AWConstants,parent=None)
	writerText.show()
	# print 'self.dictionnary : ',writerText.dictionnary.keys()

	sys.exit(app.exec_())
	
			
