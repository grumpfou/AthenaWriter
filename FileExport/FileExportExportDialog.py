from PyQt4 import QtGui, QtCore
from FileExportExport import FEList
import os


class FEExportDialog(QtGui.QDialog):
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
		self.lineedit_title = QtGui.QLineEdit ()
		self.lineedit_author = QtGui.QLineEdit ()
		self.lineedit_version = QtGui.QLineEdit ()
		
		button_export = QtGui.QPushButton("&Export")
		button_cancel = QtGui.QPushButton("&Cancel")
		button_browse = QtGui.QPushButton("&Browse")
		
		layout_path = QtGui.QHBoxLayout()
		layout_path .addWidget(self.lineedit_path )
		layout_path .addWidget(button_browse )
		
		layout_button =  QtGui.QHBoxLayout()
		layout_button.addWidget( button_export )
		layout_button.addWidget( button_cancel )
		
		
		# fill the fileds
		list_extension = [format.extension for format in FEList]
		self.combo_format.addItems(list_extension)
		self.lineedit_path.setText(default_path)
		if metadata != None and not metadata.isEmpty(): 
			d =	metadata.getDict()
			self.lineedit_title.setText(	d.get('title',""))
			self.lineedit_author.setText(	d.get('author',""))
			self.lineedit_version.setText(	d.get('version',""))
		

		# Create Main Layout
		main_layout=QtGui.QFormLayout()
		main_layout.addRow(u'Format'	,self.combo_format)
		main_layout.addRow(u'Path'		,layout_path)
		main_layout.addRow(u'Title'		,self.lineedit_title)
		main_layout.addRow(u'Author'	,self.lineedit_author)
		main_layout.addRow(u'Version'	,self.lineedit_version)
		main_layout.addRow(layout_button)
		
		
		self. setLayout ( main_layout )

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
			d['title'] 			= unicode(dialog.lineedit_title.text())
			d['author'] 		= unicode(dialog.lineedit_author.text())
			d['version'] 		= unicode(dialog.lineedit_version.text())
			return d	
		else:
			return False
		
		
# 		########################
#     def __init__(self, parent = None):
#         super(DateDialog, self).__init__(parent)
# 
#         layout = QVBoxLayout(self)
# 
#         # nice widget for editing the date
#         self.datetime = QDateTimeEdit(self)
#         self.datetime.setCalendarPopup(True)
#         self.datetime.setDateTime(QDateTime.currentDateTime())
#         layout.addWidget(self.datetime)
# 
#         # OK and Cancel buttons
#         self.buttons = QDialogButtonBox(
#             QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
#             Qt.Horizontal, self)
#         self.layout.addWidget(self.buttons)
# 
#     # get current date and time from the dialog
#     def dateTime(self):
#         return self.datetime.dateTime()
# 
#     # static method to create the dialog and return (date, time, accepted)
#     @staticmethod
#     def getDateTime(parent = None):
#         dialog = DateDialog(parent)
#         result = dialog.exec_()
#         date = dialog.dateTime()
#         return (date.date(), date.time(), result == QDialog.Accepted)
	
	# def SLOT_find(self):
		
		# pattern=unicode(self.find_line.text())
		# if pattern==u"": return False
		
		# if self.regexp_checkbox.isChecked() :
			# pattern = QtCore.QRegExp(pattern)
		# flags=None
		# if self.casse_checkbox.isChecked() or self.entireword_checkbox.isChecked():
			# if not self.casse_checkbox.isChecked():
				# flags =  QtGui.QTextDocument.FindWholeWords
			# elif not self.entireword_checkbox.isChecked():
				# flags = QtGui.QTextDocument.FindCaseSensitively
			# else :
				# flags =  QtGui.QTextDocument.FindWholeWords | QtGui.QTextDocument.FindCaseSensitively
		
		# we find all the pattern in the list
		# self.results_list=[]
		# cursor = QtGui.QTextCursor(self.textedit.document())
		# if flags==None:
			# cursor = self.textedit.document().find(pattern,cursor)
		# else:
			# cursor = self.textedit.document().find(pattern,cursor,flags)
		# self.textedit.document().find(pattern,cursor)
		# while not cursor.isNull(): 
			# cursor_context = QtGui.QTextCursor(cursor)
			# selection_lenght = cursor.selectionEnd () - cursor.selectionStart ()
			# cursor_context.setPosition(cursor.selectionStart ())
			# cursor_context.clearSelection()
			# cursor_context.movePosition (QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor,
							# TEConstants["FIND_LEN_CONTEXT"])
			# cursor_context.movePosition (QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,
							# 2*TEConstants["FIND_LEN_CONTEXT"]+selection_lenght)
			
			# context = cursor_context.selectedText ()
			
			# self.results_list.append([cursor,context])
			
			# if flags==None:
				# cursor = self.textedit.document().find(pattern,cursor)
			# else:
				# cursor = self.textedit.document().find(pattern,cursor,flags)
		
		
		# self.display_results_list()
		
	
	# def SLOT_activated(self,item):
		# cursor = self.results_list[self.tableResults.row(item)][0]
		# self.textedit.setTextCursor (cursor)
	
	# def display_results_list(self):
		# """
		# Function that is called to display the results contained in self.results_list.
		# """
		# self.tableResults.clearContents  ()	
		# self.tableResults.setRowCount(len(self.results_list))
		# for i,res in enumerate(self.results_list):
			# item_context = QtGui.QTableWidgetItem (unicode(u"..."+res[1]+u"... "))
			# item_context .setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
			# self.tableResults.setItem(i,0,item_context )
		# self.tableResults.resizeColumnsToContents()
		
	# def activate_next(self,count=1):
		# """
		# - decay : count how many occurence we must move (can be negative)"""
		# if self.tableResults.rowCount()==0:
			# return False
		# selectedItems = self.tableResults.selectedItems ()
		# if len(selectedItems) == 0:
			# item = self.tableResults.item (0,0)
		# else:
			# next_row = (self.tableResults.currentRow()+count)%\
												# self.tableResults.rowCount()
			# item = self.tableResults.item(next_row,0)
		
		# self.tableResults.setCurrentItem ( item )
		# self.SLOT_activated(item)
		# return True
		
	# def activate_previous(self):
		# self.activate_next(count=-1)
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)

	d = FEExportDialog()
	print d.getFields()
	d.close()
	import sys
	sys.exit(app.exec_())
	
	
						
	