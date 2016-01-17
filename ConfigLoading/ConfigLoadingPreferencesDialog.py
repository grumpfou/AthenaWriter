from PyQt4 import QtGui, QtCore
import copy

# DEBUG TO CHANGE !!!!
import sys,os
d,f = os.path.split(__file__)
d = os.path.join(d,'..')
sys.path.append(os.path.abspath(d))
from ConstantsManager.ConstantsManagerWidget import CMWidget

	

class CLPreferencesDialog (QtGui.QDialog):
	"""
	This calass will produce a dialog window that will allow to change the 
	preferences graphically.
	"""
	def __init__(self,dict_preferences,  *args,**kargs):
		"""
		- dict_preferences: a dictionarry that contains all the lists.
		"""
		QtGui.QDialog.__init__(self,*args,**kargs)
		self.dict_preferences 		= dict_preferences
		
		
		button_ok 		= QtGui.QPushButton('Save')
		button_cancel	= QtGui.QPushButton('Cancel')
		
		tab_widget = QtGui.QTabWidget()
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(tab_widget)
		mainLayout.addWidget(button_ok)
		mainLayout.addWidget(button_cancel)
		
		
		self.setLayout(mainLayout)
		
		self.wid_list = []
		for m,c in self.dict_preferences.items():
			w = CMWidget(constants_manager = c.copy(replace_defaults=True))
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
		self.new_dict={}
		for w,k in zip(self.wid_list,self.dict_preferences.keys()):
			d = w.getValueDict(skip_same_as_init=True)
			self.new_dict.update({k+'.'+kk:vv for kk,vv in d.items()})
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
	
			
