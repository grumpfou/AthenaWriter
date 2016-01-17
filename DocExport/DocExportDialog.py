from PyQt4 import QtGui, QtCore
from DocExportPreferences import DEPreferences
from DocExport import DEList,DEDict
from ConstantsManager.ConstantsManagerWidget import CMWidget
from ConstantsManager.ConstantsManager import CMConstantsManager

import os


class DEDialog(QtGui.QDialog):
	keys_list = 	['title','author','version']
	def __init__(self,dft_opening_saving_site=None,
				default_path='./Untitled.txt',*args,**kargs):
		"""
		A dialog window to deal with the exportations.
		"""
		if dft_opening_saving_site==None: dft_opening_saving_site=""
		self.dft_opening_saving_site = dft_opening_saving_site
		QtGui.QDialog.__init__(self,*args,**kargs)
		
		self.combo_format = QtGui.QComboBox ( self )
		self.lineedit_path = QtGui.QLineEdit ()
		self.widget_options = QtGui.QWidget()
		self.check_typo = QtGui.QCheckBox()
		self.check_typo.setToolTip('Recheck typo before export')
		
		
		# self.lineedit_title = QtGui.QLineEdit ()
		# self.lineedit_author = QtGui.QLineEdit ()
		# self.lineedit_version = QtGui.QLineEdit ()
		
		button_export = QtGui.QPushButton("&Export")
		button_cancel = QtGui.QPushButton("&Cancel")
		button_browse = QtGui.QPushButton("&Browse")
		
		layout_path = QtGui.QHBoxLayout()
		layout_path .addWidget(self.lineedit_path )
		layout_path .addWidget(button_browse )
		
		layout_button =  QtGui.QHBoxLayout()
		layout_button.addWidget( button_export )
		layout_button.addWidget( button_cancel )
		
		
		
		self.main_layout=QtGui.QFormLayout()
		self.main_layout.addRow(u'Format',self.combo_format)
		self.main_layout.addRow(u'Path'	,layout_path)
		self.main_layout.addRow(self.widget_options)
		self.main_layout.addRow(u'Recheck Typo',self.check_typo)
		
		self.rowWidgetOption = self.main_layout.rowCount()-1
		self.main_layout.addRow(layout_button)
		self.setLayout ( self.main_layout )
		
		
		
		# # fill the fileds
		list_extension = DEDict.keys()
		self.combo_format.addItems(list_extension)
		self.lineedit_path.setText(default_path)

		# Connections:
		self.connect(button_export,QtCore.SIGNAL("clicked()"),self.accept)
		self.connect(button_cancel,QtCore.SIGNAL("clicked()"),self.reject)
		self.connect(button_browse,QtCore.SIGNAL("clicked()"),self.SLOT_browse)
		self.connect(
				self.combo_format,
				QtCore.SIGNAL("activated ( const QString  )"), 
				self.SLOT_comboChanged
				)
		# to put filepath to the correct extension :
		self.SLOT_comboChanged(self.combo_format.currentText()) 
		
		
	################################## SLOTS ##################################
	def SLOT_browse(self):
		dialog= QtGui.QFileDialog(self)
		extension = DEDict[unicode(self.combo_format.currentText())].extension
		filepath = dialog.getSaveFileName(self,"Select the file to save",
			directory = self.dft_opening_saving_site,
			filter='*.'+extension)
		if filepath:
			self.lineedit_path.setText(filepath)
			
	def SLOT_comboChanged(self,text):
		ext = DEDict[unicode(text)].extension
		filepath = unicode(self.lineedit_path.text())
		filepath,tmp = os.path.splitext(filepath)
		filepath += '.' + ext
		self.lineedit_path.setText(filepath)
		
		# TODO: problem when delete
		self.widget_options.hide()
		
		# replace the same filed of the new doc_opt_dft by the old ones
		doc_opt_dft = DEDict[unicode(text)].doc_opt_dft.copy()
		if isinstance(self.widget_options,CMWidget):
			d = self.widget_options.getValueDict()
			for k, v in d.items():
				if k in doc_opt_dft.keys():
					doc_opt_dft[k] = (doc_opt_dft[k][0],v,
												doc_opt_dft[k][2]) 
		cm = CMConstantsManager.new_from_defaults(doc_opt_dft,keys_list=self.keys_list)
		self.widget_options = CMWidget(cm())
		self.main_layout.insertRow(self.rowWidgetOption,self.widget_options)
	###########################################################################
		
	# static method to create the dialog and return (date, time, accepted)
	@staticmethod
	def getFields(*args,**kargs):
		dialog = DEDialog(*args,**kargs)
		result = dialog.exec_()
		
		if result == QtGui.QDialog.Accepted:

			# def f (r):
				# r = unicode(r)
				# if r=="" : return None
				# return r
			d ={}
			d['format_name']	= unicode(dialog.combo_format.currentText())
			d['filepath']		= unicode(dialog.lineedit_path.text())
			d['check_typo']		= (dialog.check_typo.checkState() == \
															QtCore.Qt.Checked)
			dd = dialog.widget_options.getValueDict()
			d = dict(d.items()+dd.items())
			return d	
		else:
			return False
		
		
		
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)

	# d = FEExportDialog()
	print DEDialog.getFields()
	# d.close()
	import sys
	sys.exit()
	
	
						
	
