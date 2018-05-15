from PyQt5 import QtGui, QtCore, QtWidgets
from .DocExportPreferences import DEPreferences
from .DocExport import DEList,DEDict
from ConstantsManager.ConstantsManagerWidget import CMWidget
from ConstantsManager.ConstantsManager import CMConstantsManager

import os


class DEDialog(QtWidgets.QDialog):
	keys_list = 	['title','author','version']
	def __init__(self,dft_opening_saving_site=None,
				default_path='./Untitled.txt',source_d=None,*args,**kargs):
		"""
		A dialog window to deal with the exportations.
		source_d: the default arguments
		"""
		if dft_opening_saving_site==None: dft_opening_saving_site=""
		self.dft_opening_saving_site = dft_opening_saving_site
		QtWidgets.QDialog.__init__(self,*args)

		self.combo_format = QtWidgets.QComboBox ( self )
		self.lineedit_path = QtWidgets.QLineEdit ()
		self.widget_options = QtWidgets.QWidget()
		self.check_typo = QtWidgets.QCheckBox()
		self.check_typo.setToolTip('Recheck typo before export')


		# self.lineedit_title = QtWidgets.QLineEdit ()
		# self.lineedit_author = QtWidgets.QLineEdit ()
		# self.lineedit_version = QtWidgets.QLineEdit ()

		button_export = QtWidgets.QPushButton("&Export")
		button_cancel = QtWidgets.QPushButton("&Cancel")
		button_browse = QtWidgets.QPushButton("&Browse")

		layout_path = QtWidgets.QHBoxLayout()
		layout_path .addWidget(self.lineedit_path )
		layout_path .addWidget(button_browse )

		layout_button =  QtWidgets.QHBoxLayout()
		layout_button.addWidget( button_export )
		layout_button.addWidget( button_cancel )

		self.main_layout=QtWidgets.QFormLayout()
		self.main_layout.addRow('Format',self.combo_format)
		self.main_layout.addRow('Path'	,layout_path)
		self.main_layout.addRow(self.widget_options)
		self.main_layout.addRow('Recheck Typo',self.check_typo)

		self.rowWidgetOption = self.main_layout.rowCount()-1
		self.main_layout.addRow(layout_button)
		self.setLayout ( self.main_layout )

		# def
		if source_d==None: source_d={}
		self.source_d = CMConstantsManager.new_from_defaults(
										source_d,keys_list=self.keys_list)()


		# # fill the fileds
		list_extension = list(DEDict.keys())
		self.combo_format.addItems(list_extension)
		self.lineedit_path.setText(default_path)

		# Connections:
		button_export.clicked.connect(self.accept)
		button_cancel.clicked.connect(self.reject)
		button_browse.clicked.connect(self.SLOT_browse)
		self.combo_format.activated[str] .connect(
				self.SLOT_comboChanged
				)
		# to put filepath to the correct extension :
		self.SLOT_comboChanged(self.combo_format.currentText(),
															source_d=source_d)



	################################## SLOTS ##################################
	def SLOT_browse(self):
		dialog= QtWidgets.QFileDialog(self)
		extension = DEDict[str(self.combo_format.currentText())].extension
		filepath = dialog.getSaveFileName(self,"Select the file to save",
			directory = self.dft_opening_saving_site,
			filter='*.'+extension)[0]
		if filepath:
			self.lineedit_path.setText(filepath)

	def SLOT_comboChanged(self,text,source_d=None):
		ext = DEDict[str(text)].extension
		filepath = str(self.lineedit_path.text())
		filepath,tmp = os.path.splitext(filepath)
		filepath += '.' + ext
		self.lineedit_path.setText(filepath)

		# TODO: problem when delete
		self.widget_options.hide()

		# replace the same filed of the new doc_opt by the old ones
		doc_opt = DEDict[str(text)].doc_opt.copy()
		if isinstance(self.widget_options,CMWidget):
			d = self.widget_options.getValueDict()
			for k, v in list(d.items()):
				if k in list(doc_opt.keys()):
					doc_opt[k] = doc_opt[k]
		if source_d!=None:
			for k, v in list(source_d.items()):
				if k in list(doc_opt.keys()):
					doc_opt[k] = v

		cm = CMConstantsManager.new_from_defaults(doc_opt,keys_list=self.keys_list)
		self.widget_options = CMWidget(cm())
		self.main_layout.insertRow(self.rowWidgetOption,self.widget_options)
	###########################################################################

	# static method to create the dialog and return (date, time, accepted)
	@staticmethod
	def getFields(*args,**kargs):
		dialog = DEDialog(*args,**kargs)
		result = dialog.exec_()

		if result == QtWidgets.QDialog.Accepted:

			# def f (r):
				# r = unicode(r)
				# if r=="" : return None
				# return r
			d ={}
			d['format_name']	= str(dialog.combo_format.currentText())
			d['filepath']		= str(dialog.lineedit_path.text())
			d['check_typo']		= (dialog.check_typo.checkState() == \
															QtCore.Qt.Checked)
			dd = dialog.widget_options.getValueDict()
			d = dict(list(d.items())+list(dd.items()))
			return d
		else:
			return False



if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)

	# d = FEExportDialog()
	print(DEDialog.getFields())
	# d.close()
	import sys
	sys.exit()
