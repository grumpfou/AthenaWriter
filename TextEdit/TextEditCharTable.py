"""
Part of the WolfWriter project. Written by Renaud Dessalles
This file decribe the creation of the widget of the Char table
"""

from PyQt5 import QtGui, QtCore, QtWidgets
ii = lambda s : int(s,16)

class TECharWidgetTable(QtWidgets.QWidget):
	# the list of the fields (to have them in a given order)
	list_char_fields=[	"Basic Latin","Latin-1 Supplement","Latin Extended-A","Latin Extended-B",\
						"IPA Extensions","Spacing Modifier Letters","Greek","Cyrillic","Latin Extended Additional",\
						"Greek Extended","General Punctuation","Superscripts and Subscripts","Currency Symbols",\
						"Letterlike Symbols","Number Forms","Arrows","Mathematical Operators","Miscellaneous Technical",\
						"Box Drawing","Block Elements","Geometric Shapes","Miscellaneous Symbols","Private Use Area",\
						"Alphabetic Presentation Forms","Double Struck"]

	# the diconary of the fields : to every field it gives the range of the of the chars adress to consider.
	# (source : https://en.wikipedia.org/wiki/Unicode)
	dico_char_ranges=\
		{"Basic Latin"					:(ii('0020'), ii('007F')),\
		"Latin-1 Supplement"			:(ii('0080'), ii('00FF')),\
		"Latin Extended-A"				:(ii('0100'), ii('017F')),\
		"Latin Extended-B"				:(ii('0180'), ii('024F')),\
		"IPA Extensions"				:(ii('0250'), ii('02AF')),\
		"Spacing Modifier Letters"		:(ii('02B0'), ii('02FF')),\
		"Greek"							:(ii('0370'), ii('03FF')),\
		"Cyrillic"						:(ii('0400'), ii('04FF')),\
		"Latin Extended Additional"		:(ii('1E00'), ii('1EFF')),\
		"Greek Extended"				:(ii('1F00'), ii('1FFF')),\
		"General Punctuation"			:(ii('2000'), ii('206F')),\
		"Superscripts and Subscripts"	:(ii('2070'), ii('209F')),\
		"Currency Symbols"				:(ii('20A0'), ii('20CF')),\
		"Letterlike Symbols"			:(ii('2100'), ii('214F')),\
		"Number Forms"					:(ii('2150'), ii('218F')),\
		"Arrows"						:(ii('2190'), ii('21FF')),\
		"Mathematical Operators"		:(ii('2200'), ii('22FF')),\
		"Miscellaneous Technical"		:(ii('2300'), ii('23FF')),\
		"Box Drawing"					:(ii('2500'), ii('257F')),\
		"Block Elements"				:(ii('2580'), ii('259F')),\
		"Geometric Shapes"				:(ii('25A0'), ii('25FF')),\
		"Miscellaneous Symbols"			:(ii('2600'), ii('26FF')),\
		"Private Use Area"				:(ii('F000'), ii('F0FF')),\
		"Alphabetic Presentation Forms"	:(ii('FB00'), ii('FB4F')),\
		"Double Struck"					:[	ii('1D538'), ii('1D539'), ii('02102'), ii('1D53B'), ii('1D53C'), 
											ii('1D53D'), ii('1D53E'), ii('0210D'), ii('1D540'), ii('1D541'), 
											ii('1D542'), ii('1D543'), ii('1D544'), ii('02115'), ii('1D546'), 
											ii('02119'), ii('0211A'), ii('0211D'), ii('1D54A'), ii('1D54B'), 
											ii('1D54C'), ii('1D54D'), ii('1D54E'), ii('1D54F'), ii('1D550'), 
											ii('02124'), ii('1D552'), ii('1D553'), ii('1D554'), ii('1D555'), 
											ii('1D556'), ii('1D557'), ii('1D558'), ii('1D559'), ii('1D55A'), 
											ii('1D55B'), ii('1D55C'), ii('1D55D'), ii('1D55E'), ii('1D55F'), 
											ii('1D560'), ii('1D561'), ii('1D562'), ii('1D563'), ii('1D564'), 
											ii('1D565'), ii('1D566'), ii('1D567'), ii('1D568'), ii('1D569'), 
											ii('1D56A'), ii('1D56B'), ii('1D7D8'), ii('1D7D9'), ii('1D7DA'), 
											ii('1D7DB'), ii('1D7DC'), ii('1D7DD'), ii('1D7DE'), ii('1D7DF'), 
											ii('1D7E0'), ii('1D7E1'),
										]}
		
		
	
	def __init__(self,linked_text_widget=None,nb_columns=16,*args,**kargs):
		"""
		The Wiget that will will contain the TECharTable. It allows to choose the file.
		TODO : a direct code access of the char.
		- linked_text_widget : A TextEdit or LineEdit instance where to add the 
				chosen chars
		- nb_columns : the number of columns to display in the CharTable
		"""
		QtWidgets.QWidget.__init__(self,*args,**kargs)
		self.linked_text_widget=linked_text_widget
		self.comboBox = QtWidgets.QComboBox() # will contain the field list
		self.charTable=TECharTable(nb_columns=nb_columns)
		for k in self.list_char_fields: # We add the field name to the comboBox
			self.comboBox.addItem(k)
		
		self.comboBox.currentIndexChanged.connect( self.SLOT_changeTable)
		self.charTable.itemActivated.connect( self.SLOT_itemActivated)
		layout=QtWidgets.QVBoxLayout()
		layout.addWidget( self.comboBox )
		layout.addWidget( self.charTable )
		self.setLayout ( layout )
		
		w = self.charTable.horizontalHeader().length()
		size = self.size()
		size.setWidth (w)
		self.resize(size)		
		
	
	def SLOT_changeTable(self):
		"""
		Slot called when changing the field in the comboBox to apply it in the  	
		TECharTable.
		"""
		field=str(self.comboBox.itemText(self.comboBox.currentIndex()))
		self.charTable.changeRange(self.dico_char_ranges[field])

	def SLOT_itemActivated(self,item):
		"""Slot called when a char of the table is activated. It insert the selected 
		char in the corresponding linked_text_widget """
		if self.linked_text_widget!=None:
			if isinstance(self.linked_text_widget,QtWidgets.QTextEdit):
				self.linked_text_widget.insertPlainText(item.text())
			if isinstance(self.linked_text_widget,QtWidgets.QLineEdit):
				self.linked_text_widget.insert(item.text())
			


		
class TECharTable (QtWidgets.QTableWidget):
	
	def __init__(self,nb_columns=16,range_char=(int('0020',16),int('024F',16))):
		"""
		A re-implementation of QTableWidget. It will display all the chars contained 
		in the given range.
		- nb_columns : number of columns to display
		- range_char : a tuple that contains the borns of the field range to display.
		Note : range_char=(0,10) includes 10.
		"""
		self.nb_columns=nb_columns
		QtWidgets.QTableWidget.__init__(self)
		self.setColumnCount(self.nb_columns)
		self.changeRange(range_char)
		
	def changeRange(self,range_char):
		"""Method that is called when changing the range of the chars"""
		if type(range_char)==tuple:
			size=(range_char[1]+1)-range_char[0]
			rge = list(range(range_char[0],range_char[1]+1))
		elif type(range_char)==list:
			size= len(range_char)
			rge = range_char
			
		self.setRowCount((size/self.nb_columns)+1)
		for i,char_nb in enumerate(rge):
			item = QtWidgets.QTableWidgetItem (chr(char_nb))
			item.setTextAlignment (QtCore.Qt.AlignCenter)
			item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
			self.setItem(i/self.nb_columns,i%self.nb_columns,item)
		self.resizeRowsToContents()
		self.resizeColumnsToContents()
	

		
if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	
	widTable = TECharWidgetTable()	
	
	main_window=QtWidgets.QMainWindow()
	main_window.setCentralWidget(widTable)

	main_window.show()
	sys.exit(app.exec_())
	# sys.exit(textedit.exec_())
