from PyQt4 import QtGui, QtCore
from FileExportExport import FEList,FEDict
import os


class FEExportDialog(QtGui.QDialog):
	key_list = 	['title','author','version']
	def __init__(self,metadata=None,dft_opening_saving_site=None,
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
		self.main_layout.addRow(u'Format'	,self.combo_format)
		self.main_layout.addRow(u'Path'		,layout_path)
		self.main_layout.addRow(self.widget_options)
		
		self.rowWidgetOption = self.main_layout.rowCount()-1
		self.main_layout.addRow(layout_button)
		self.setLayout ( self.main_layout )
		
		
		
		# # fill the fileds
		list_extension = FEDict.keys()
		self.combo_format.addItems(list_extension)
		self.lineedit_path.setText(default_path)
		# if metadata != None and not metadata.isEmpty(): 
			# d =	metadata.getDict()
			# self.lineedit_title.setText(	d.get('title',""))
			# self.lineedit_author.setText(	d.get('author',""))
			# self.lineedit_version.setText(	d.get('version',""))
		# 
		# 
		# # Create Main Layout
		# main_layout=QtGui.QFormLayout()
		# main_layout.addRow(u'Format'	,self.combo_format)
		# main_layout.addRow(u'Path'		,layout_path)
		# main_layout.addRow(u'Title'		,self.lineedit_title)
		# main_layout.addRow(u'Author'	,self.lineedit_author)
		# main_layout.addRow(u'Version'	,self.lineedit_version)
		# main_layout.addRow(layout_button)
		# 
		# 
		# self. setLayout ( main_layout )

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
		extension = self.combo_format.currentText ()
		filepath = dialog.getSaveFileName(self,"Select the file to save",
			directory = self.dft_opening_saving_site,
			filter='*.'+extension)
		if filepath:
			self.lineedit_path.setText(filepath)
			
	def SLOT_comboChanged(self,text):
		filepath = unicode(self.lineedit_path.text())
		filepath,ext = os.path.splitext(filepath)
		filepath += '.' + text
		self.lineedit_path.setText(filepath)
		
		# TODO: problem when delete
		self.widget_options.hide()
		
		# replace the same filed of the new document_options by the old ones
		document_options = FEDict[unicode(text)].document_options.copy()
		if isinstance(self.widget_options,FEWidget):
			d = self.widget_options.getValueDict()
			for k, v in d.items():
				if k in document_options.keys():
					document_options[k] = (document_options[k][0],v,
												document_options[k][2]) 
		self.widget_options = FEWidget(document_options,key_list=self.key_list)
		self.main_layout.insertRow(self.rowWidgetOption,self.widget_options)
	###########################################################################
		
	# static method to create the dialog and return (date, time, accepted)
	@staticmethod
	def getFields(*args,**kargs):
		dialog = FEExportDialog(*args,**kargs)
		result = dialog.exec_()
		
		if result == QtGui.QDialog.Accepted:

			# def f (r):
				# r = unicode(r)
				# if r=="" : return None
				# return r
			d ={}
			d['format_name']	= unicode(dialog.combo_format.currentText())
			d['filepath']		= unicode(dialog.lineedit_path.text())
			dd = dialog.widget_options.getValueDict()
			d = dict(d.items()+dd.items())
			return d	
		else:
			return False
		
		
		
		
		

doubleSpinBoxStep = .1

class FEWidget (QtGui.QWidget):
	def __init__(self,constants_dict,widget_dict=None,key_list=None,
			constraints_dict=None,overwrite_dict=None,*args,**kargs):
		""" This class will manage the constants with a gui interface. Each
		constant is caracterized by its name (called key), its type, its 
		initial value and its description. These information are given in 
		constants_dict.
		
		- constants_dict under the form:
			{key : ( type, current_value ,decr) ,...}
		- widget_dict under the form:
			{key :  widget_to_display ,...}
		- key_list : list of key in the order to be displayed
		- constraints : for each type its constraint
			int : (min,max,interval)
			float : (min,max,interval)
			
			Should be under the form:
			{key :  (constraints1, constraints2, ...) ,...}
		
		"""
		QtGui.QDialog.__init__(self,*args,**kargs)
		
		if key_list == None : key_list =[]
		if widget_dict == None : widget_dict ={}
		if constraints_dict == None : constraints_dict ={}
		
		self.keys = key_list[:]
		print 'self.keys : ',self.keys
		self.constants_dict = constants_dict
		self.constraints_dict = constraints_dict
		self.widget_dict = {}
		self.initial_dict = {k : v[1] for k,v in self.constants_dict.items()}
		
		keys_of_constants_dict = self.constants_dict.keys()
		for k in self.keys:
			print 'k : ',k
			try :
				keys_of_constants_dict.pop(keys_of_constants_dict.index(k))
			except ValueError:
				raise ValueError('The key ',k,' of key_list should be a key '+\
						'of contants_dict')
		keys_of_constants_dict.sort()
		self.keys += keys_of_constants_dict
		print 'self.keys : ',self.keys
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
		"""Will give the widget correponding to a certain type of constant:
		- key : the key of the constant.
			will work for basic constant type, there is
		
		"""
		type_ = self.constants_dict[key][0]
		value = self.constants_dict[key][1]
		descr = self.constants_dict[key][2]
		if type_ == bool :
			wid = QtGui.QCheckBox ( parent = self )
			if value:
				wid.setCheckState(QtCore.Qt.Checked)
			else:
				wid.setCheckState(QtCore.Qt.Unchecked)
		elif type_ == int or type_ == float :
			if type_ == int:
				wid = QtGui.QSpinBox ( parent = self )
			else:
				wid = QtGui.QDoubleSpinBox ( parent = self )
				
			if self.constraints_dict.has_key(key):
				c = self.constraints_dict[k]
				if c[0]!=None:
					wid.setMinimum ( c[0] )
				if c[1]!=None:
					wid.setMaximum ( c[1] )
				if c[2]!=None:
					wid.setSingleStep ( c[2] )
				elif type_ == float:
					wid.setSingleStep ( doubleSpinBoxStep )
			elif type_ == float:
					wid.setSingleStep ( doubleSpinBoxStep )
			wid.setValue(value)
			
		elif type_ in [str,unicode]:
			wid = QtGui.QLineEdit ( parent = self )
			wid.setText(value)
		else:
			import textwrap
			msg = textwrap.fill(\
				'The type of the constant '+key+' is not convertible into a '+\
				'widget, use the widget_dict to set your own.')
			raise TypeError(msg)
		wid.setToolTip(descr)
		return wid
			
		
	def getValue(self,key):
		"""Will return the value of the constant of the correponding key"""
		type_ = self.constants_dict[key][0]
		value = self.constants_dict[key][1]
		descr = self.constants_dict[key][2]
		wid = self.widget_dict[key]
		if type_ == bool :
			wid = self.widget_dict[key]
			if wid.checkState () == QtCore.Qt.Checked:
				return True
			else :
				return False
		elif type_ == int or type_ == float :
			return	type_(wid.value())
			
		elif type_ in [str,unicode]:
			return type_(wid.text())
	
	def getValueDict(self,skip_same_as_init=False):
		"""Will return the dictionary of the values
		- skip_same_as_init : if True, will return only the one that have 
				changed since the begining.
		"""
		res = {}
		print 'coucou'
		for k in self.keys:
			v = self.getValue(k)
			if (not skip_same_as_init) or v!=self.initial_dict[k]:
				print 'k,v : ',k,v
				res[k]=v
		
		return res
		
		
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)

	# d = FEExportDialog()
	print FEExportDialog.getFields()
	# d.close()
	import sys
	sys.exit()
	
	
						
	