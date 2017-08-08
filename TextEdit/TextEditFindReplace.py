from PyQt5 import QtGui, QtCore, QtWidgets

from .TextEditPreferences 	import *
from CommonObjects.CommonObjectsWord		import COWordTools


# add a simple function to the QCheckBox that return the checked state of the CheckBox
def isChecked_WW(self):
	# assert not self.isTristate
	assert not self.isTristate()
	if self.checkState () == QtCore.Qt.Checked:
		return True
	else :
		return False
QtWidgets.QCheckBox.isChecked=isChecked_WW

class TEFindDialog(QtWidgets.QDialog):
	def __init__(self,textedit,*args,**kargs):
		"""
		This function will display a window to find for partern in the textedit file.
		textedit : the textedit instance in which we have to find
		"""
		QtWidgets.QDialog.__init__(self,parent=textedit,*args,**kargs)
		self.textedit = textedit
		
		self.find_line		= QtWidgets.QLineEdit ()
		self.replace_line	= QtWidgets.QLineEdit ()
		
		# Options check boxes:
		self.casse_checkbox = QtWidgets.QCheckBox()
		self.regexp_checkbox = QtWidgets.QCheckBox()
		self.entireword_checkbox = QtWidgets.QCheckBox()
		
		find_button = QtWidgets.QPushButton("&Find")
		replace_button = QtWidgets.QPushButton("&Replace")
		replaceall_button = QtWidgets.QPushButton("&Replace All")
		# find_button.setIcon(QtGui.QIcon(os.path.join(abs_path_icon,"find.png")))
		
		# The table were the results are displayed
		self.tableResults = QtWidgets.QTableWidget(0,1)
		# self.tableResults.setHorizontalHeaderLabels([u"Line",u"Context"])
		self.tableResults.setSelectionBehavior (QtWidgets.QAbstractItemView.SelectRows)
		self.tableResults.horizontalHeader ().setVisible(False)
		self.tableResults.horizontalHeader ().setStretchLastSection(True)
		
		main_layout=QtWidgets.QFormLayout()
		main_layout.addRow(self.find_line,find_button)
		main_layout.addRow(self.replace_line ,replace_button)
		main_layout.addRow(None ,replaceall_button)
		main_layout.addRow("Casse sensitive",self.casse_checkbox)
		main_layout.addRow("Regular expression",self.regexp_checkbox)
		main_layout.addRow("Entire word",self.entireword_checkbox)
		main_layout.addRow(self.tableResults)
		
		self. setLayout ( main_layout )

		# Connections:
		find_button.clicked.connect( self.SLOT_find)
		self.find_line.returnPressed  .connect( self.SLOT_find)
		replace_button.clicked.connect( self.SLOT_replace)
		replaceall_button.clicked.connect( self.SLOT_replaceall)
		self.tableResults.itemActivated   .connect( self.SLOT_activated)
		
		self.results_list=[]
		
	def SLOT_find(self):
		
		pattern=str(self.find_line.text())
		if pattern=="": return False
		
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
			cursor_context.movePosition (QtGui.QTextCursor.Left,
					QtGui.QTextCursor.MoveAnchor,
					TEPreferences["FIND_LEN_CONTEXT"])
			cursor_context.movePosition (QtGui.QTextCursor.Right,
					QtGui.QTextCursor.KeepAnchor,
					2*TEPreferences["FIND_LEN_CONTEXT"]+selection_lenght)
			
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
	
	def SLOT_replace(self,count=1):
		if self.tableResults.rowCount()==0:
			return False
		selectedItems = self.tableResults.selectedItems ()
		if len(selectedItems) == 0:
			item = self.tableResults.item (0,0)
			self.tableResults.setCurrentItem ( item )
			self.SLOT_activated(item)
		else:
			item = self.tableResults.currentItem()
			cursor = self.results_list[self.tableResults.row(item)][0]
			if cursor.hasSelection():
				next_text = str(self.replace_line.text())
				if not self.casse_checkbox.isChecked():
					previous_text = str(cursor.selection().toPlainText())
					id = COWordTools.whatID(previous_text)
					next_text = COWordTools.toID(next_text,id)				
				cursor.insertText(next_text)
			self.activate_next()
				
		
		
	def SLOT_replaceall(self):
		self.SLOT_find()
		if self.tableResults.rowCount()==0:
			msg= 'No occurance of "'+str(self.find_line.text())+'" found.'
			dia = QtWidgets.QMessageBox.information ( 
							self, 
							"Exportation" , 
							msg)
			return False
			
		item = self.tableResults.item (0,0)
		self.tableResults.setCurrentItem ( item )
		self.SLOT_activated(item)
		rcount = self.tableResults.rowCount()
		for i in range(rcount):
			self.SLOT_replace()
	
		msg= '"'+str(self.find_line.text())+'" has been replaced '+\
				str(rcount)+' times in the document.'
		dia = QtWidgets.QMessageBox.information ( 
						self, 
						"Exportation" , 
						msg)
		
		
	
	def display_results_list(self):
		"""
		Function that is called to display the results contained in self.results_list.
		"""
		self.tableResults.clearContents  ()	
		self.tableResults.setRowCount(len(self.results_list))
		for i,res in enumerate(self.results_list):
			item_context = QtWidgets.QTableWidgetItem (str("..."+res[1]+"... "))
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
	from .TextEdit import *
	
	app = QtWidgets.QApplication(sys.argv)
	
	textedit = TETextEdit(parent=None)
	find  = TEFindDialog(textedit=textedit)
	
	# textedit.connect(textedit,QtCore.SIGNAL('typographyModification ()'), stupidity)
	# textedit.emit_typographyModification()
	# textedit.typographyModification .connect( stupidity)
	# textedit.typographyModification.connect(stupidity)
	textedit.show()
	find.show()
	
	import sys
	sys.exit(app.exec_())
