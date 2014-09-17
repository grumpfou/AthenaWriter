from PyQt4 import QtGui,QtCore

from TextEditConstants 				import *



# add a simple function to the QCheckBox that return the checked state of the CheckBox
def isChecked_WW(self):
	# assert not self.isTristate
	assert not self.isTristate()
	if self.checkState () == QtCore.Qt.Checked:
		return True
	else :
		return False
QtGui.QCheckBox.isChecked=isChecked_WW

class TEFindDialog(QtGui.QDialog):
	def __init__(self,textedit,*args,**kargs):
		"""
		This function will display a window to find for partern in the textedit file.
		textedit : the textedit instance in which we have to find
		"""
		QtGui.QDialog.__init__(self,parent=textedit,*args,**kargs)
		self.textedit = textedit
		
		self.find_line	= QtGui.QLineEdit ()
		
		# Options check boxes:
		self.casse_checkbox = QtGui.QCheckBox()
		self.regexp_checkbox = QtGui.QCheckBox()
		self.entireword_checkbox = QtGui.QCheckBox()
		
		find_button = QtGui.QPushButton("&Find")
		# find_button.setIcon(QtGui.QIcon(os.path.join(abs_path_icon,"find.png")))
		
		# The table were the results are displayed
		self.tableResults = QtGui.QTableWidget(0,1)
		# self.tableResults.setHorizontalHeaderLabels([u"Line",u"Context"])
		self.tableResults.setSelectionBehavior (QtGui.QAbstractItemView.SelectRows)
		self.tableResults.horizontalHeader ().setVisible(False)
		self.tableResults.horizontalHeader ().setStretchLastSection(True)
		
		main_layout=QtGui.QFormLayout()
		main_layout.addRow(self.find_line,find_button)
		main_layout.addRow(u"Casse sensitive",self.casse_checkbox)
		main_layout.addRow(u"Regular expression",self.regexp_checkbox)
		main_layout.addRow(u"Entire word",self.entireword_checkbox)
		main_layout.addRow(self.tableResults)
		
		self. setLayout ( main_layout )

		# Connections:
		self.connect(find_button, QtCore.SIGNAL("clicked()"), self.SLOT_find)
		self.connect(self.find_line, QtCore.SIGNAL('returnPressed  ()'), self.SLOT_find)
		self.connect(self.tableResults,QtCore.SIGNAL('itemActivated   ( QTableWidgetItem * )'), self.SLOT_activated)
		
		self.results_list=[]
		
	def SLOT_find(self):
		
		pattern=unicode(self.find_line.text())
		if pattern==u"": return False
		
		if self.regexp_checkbox.isChecked() :
			pattern = QtCore.QRegExp(pattern)
		flags=None
		if self.casse_checkbox.isChecked() or self.entireword_checkbox.isChecked():
			if not self.casse_checkbox.isChecked():
				flags =  QtGui.QTextDocument.FindWholeWords
			elif not self.entireword_checkbox.isChecked():
				flags = QtGui.QTextDocument.FindCaseSensitively
			else :
				flags =  QtGui.QTextDocument.FindWholeWords | QtGui.QTextDocument.FindCaseSensitively
		
		# we find all the pattern in the list
		self.results_list=[]
		cursor = QtGui.QTextCursor(self.textedit.document())
		if flags==None:
			cursor = self.textedit.document().find(pattern,cursor)
		else:
			cursor = self.textedit.document().find(pattern,cursor,flags)
		# self.textedit.document().find(pattern,cursor)
		while not cursor.isNull(): 
			cursor_context = QtGui.QTextCursor(cursor)
			selection_lenght = cursor.selectionEnd () - cursor.selectionStart ()
			cursor_context.setPosition(cursor.selectionStart ())
			cursor_context.clearSelection()
			cursor_context.movePosition (QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor,
							TEConstants["FIND_LEN_CONTEXT"])
			cursor_context.movePosition (QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,
							2*TEConstants["FIND_LEN_CONTEXT"]+selection_lenght)
			
			context = cursor_context.selectedText ()
			
			self.results_list.append([cursor,context])
			
			if flags==None:
				cursor = self.textedit.document().find(pattern,cursor)
			else:
				cursor = self.textedit.document().find(pattern,cursor,flags)
		
		
		self.display_results_list()
		
	
	def SLOT_activated(self,item):
		cursor = self.results_list[self.tableResults.row(item)][0]
		self.textedit.setTextCursor (cursor)
	
	def display_results_list(self):
		"""
		Function that is called to display the results contained in self.results_list.
		"""
		self.tableResults.clearContents  ()	
		self.tableResults.setRowCount(len(self.results_list))
		for i,res in enumerate(self.results_list):
			item_context = QtGui.QTableWidgetItem (unicode(u"..."+res[1]+u"... "))
			item_context .setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
			self.tableResults.setItem(i,0,item_context )
		self.tableResults.resizeColumnsToContents()
		
	def activate_next(self,count=1):
		"""
		- decay : count how many occurence we must move (can be negative)"""
		if self.tableResults.rowCount()==0:
			return False
		selectedItems = self.tableResults.selectedItems ()
		if len(selectedItems) == 0:
			item = self.tableResults.item (0,0)
		else:
			next_row = (self.tableResults.currentRow()+count)%\
												self.tableResults.rowCount()
			item = self.tableResults.item(next_row,0)
		
		self.tableResults.setCurrentItem ( item )
		self.SLOT_activated(item)
		return True
		
	def activate_previous(self):
		self.activate_next(count=-1)
	
if __name__ == '__main__':
	from TextEdit import *
	
	app = QtGui.QApplication(sys.argv)
	
	textedit = TETextEdit(parent=None)
	find  = TEFindDialog(textedit=textedit)
	
	# textedit.connect(textedit,QtCore.SIGNAL('typographyModification ()'), stupidity)
	# textedit.emit_typographyModification()
	# QtCore.QObject.connect(textedit,QtCore.SIGNAL('typographyModification ()'), stupidity)
	# textedit.typographyModification.connect(stupidity)
	textedit.show()
	find.show()
	
	import sys
	sys.exit(app.exec_())