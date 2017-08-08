from PyQt5 import QtGui, QtCore, QtWidgets
import copy

# DEBUG TO CHANGE !!!!
import sys,os
d,f = os.path.split(__file__)
d = os.path.join(d,'..')
sys.path.append(os.path.abspath(d))
from ConstantsManager.ConstantsManagerWidget import CMWidget



class CLPreferencesDialog (QtWidgets.QDialog):
	"""
	This calass will produce a dialog window that will allow to change the
	preferences graphically.
	"""
	def __init__(self,dict_preferences,  *args,**kargs):
		"""
		- dict_preferences: a dictionarry that contains all the lists.
		"""
		QtWidgets.QDialog.__init__(self,*args,**kargs)
		self.dict_preferences 		= dict_preferences


		button_ok 		= QtWidgets.QPushButton('Save')
		button_cancel	= QtWidgets.QPushButton('Cancel')

		tab_widget = QtWidgets.QTabWidget()
		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.addWidget(tab_widget)
		mainLayout.addWidget(button_ok)
		mainLayout.addWidget(button_cancel)


		self.setLayout(mainLayout)

		self.wid_list = []
		for m,c in list(self.dict_preferences.items()):
			w = CMWidget(constants_manager = c.copy(replace_defaults=True))
			tab_widget.addTab(w,m)
			self.wid_list.append(w)
		self.new_dict=None

		button_ok.clicked.connect( self.SLOT_replace_constants)
		button_cancel.clicked.connect( self.close)

	def SLOT_replace_constants(self):
		self.new_dict={}
		for w,k in zip(self.wid_list,list(self.dict_preferences.keys())):
			d = w.getValueDict(skip_same_as_init=True)
			self.new_dict.update({k+'.'+kk:vv for kk,vv in list(d.items())})
		self.accept()

	@staticmethod
	def getValueDict(*args,**kargs):
		dialog = CLPreferencesDialog(*args,**kargs)
		result = dialog.exec_()
		d = dialog.new_dict

		if result == QtWidgets.QDialog.Accepted:
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

	app = QtWidgets.QApplication(sys.argv)
	writerText = CLPreferencesDialog(constants=AWConstants,parent=None)
	writerText.show()
	# print 'self.dictionnary : ',writerText.dictionnary.keys()

	sys.exit(app.exec_())
