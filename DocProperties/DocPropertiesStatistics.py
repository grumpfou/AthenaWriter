import os
import codecs

from PyQt4 import QtGui,QtCore

from DocPropertiesPreferences import *

class DPStatistics:
	"""
	List of functions that will make statistics on unicode strings.
	"""

	@staticmethod
	def lines_in_book(text_book):
		"""
		Will make a 3 deep list of words as follows:
		[  [  [  [word1],[word2],... ], [...], ... ], [...], ...]
		|  |  |_______line 1_________|             |            |   
		|  |                                       |            |   
		|  |__________bloc 1_______________________|            |   
		|                                                       |   
		|_____________book______________________________________|   
		- text_book : the unicode string to make the list.
		"""
		
		li_blocs = text_book.split('\n')
		li_lines = [DPStatistics.lines_in_bloc(bloc) for bloc in li_blocs]
		return li_lines
		
	@staticmethod
	def lines_in_bloc(text_bloc):
		"""
		Will make a 2 deep list words as follows:
		[  [  [word1],[word2],... ], [...], ... ]
		|  |_______line 1_________|             |   
		|                                       |   
		|__________bloc_________________________|   
		- text_bloc: the unicode string on which it makes the list
			(it should represent only one paragraph).														
		"""
		
		li_words  = text_bloc.split(' ')
		
		li_len_words  = [len(word) for word in li_words] #list of the length of the words
		li_len_words[0]+=DPPreferences['NB_CHAR_PER_INDENT'] # add the indent length to the first word
		
		counter = 0		
		lines =[]
		line =[]
		for i,v in enumerate(li_words):
			if counter+len(v)> DPPreferences['NB_CHAR_PER_LINE']: 
				# if it ovetakes the line then
				if counter==0: #if the word is bigger than the line
					lines_to_add = []
					for i in range(len(v)/(DPPreferences['NB_CHAR_PER_LINE']-1)+1):
						# We count -1 for the size of the breakline
						ii = i*(DPPreferences['NB_CHAR_PER_LINE']-1) 
						jj = min(len(v),
									(i+1)*(DPPreferences['NB_CHAR_PER_LINE']-1))
						w = v[ii:jj]
						if jj<len(v):
							w+='-'
							
						lines_to_add.append([w])
						
					lines += lines_to_add
					counter=len(lines_to_add[-1])
				else:
					lines.append(line)
					line = [v]
					counter=len(v)
			else :
				line.append(v)
				counter+=1+len(v) #+1 for the size of the space
		lines.append(line)
		
		return lines

	@staticmethod
	def stats(text,format=['nb_pages']):
		"""
		Will return the information asked on the unicode string.
		- text: unicode string on which the statistics are made
		- format: a list of information asked (answer will be return
			in the same order. All the elements of the list should be 
			in : ['nb_pages', 'nb_blocs', 'nb_lines', 'nb_chars_with_spaces', 'nb_chars_without_spaces','nb_words'] 
		"""
		
		lines = DPStatistics.lines_in_book(text)
		results=[]
		for ask in format:
			if ask=='nb_pages':
				lines_flat = [item for bloc in lines for item in bloc]
				q = len(lines_flat)/DPPreferences['NB_LINE_PER_PAGE']
				r = len(lines_flat)%DPPreferences['NB_LINE_PER_PAGE']
				if r>0:
					q+=1
				results.append(q)
			elif ask =='nb_blocs':
				results.append(len(lines))
			elif ask=='nb_lines':
				lines_flat = [item for bloc in lines for item in bloc]
				results.append(len(lines_flat))
			elif ask=='nb_chars_without_spaces':
				word_flat = [item for bloc in lines for line in bloc for item in line]
				res = 0
				for w in word_flat: res+=len(w)
				results.append(res)
			elif ask=='nb_chars_with_spaces':
				book = DPStatistics.shape_book(text)
				results.append(len(book))
			elif ask=='nb_words':
				word_flat1 = [item for bloc in lines for line in bloc \
															for item in line]
				word_flat2 = [word_flat1[0]]
				# we detect the cutted words
				for i in range(1,len(word_flat1)):
					w = word_flat2[-1]
					if len(w)>1 and w[-1]=='-':
						word_flat2[-1]+= word_flat1[i]
					else:
						word_flat2.append(word_flat1[i])
				results.append(len(word_flat2))
				
			else:
				raise ValueError(str(ask) + " should be in ['nb_pages', 'nb_blocs', 'nb_lines', 'nb_chars_with_spaces', 'nb_chars_without_spaces','nb_words'].")
		return results		
					
	@staticmethod
	def shape_book(text):
		"""
		This function will return the text on which we are making the statistics 
		in the function stats.
		"""
		lines = DPStatistics.lines_in_book(text)
		result=u""
		for block in lines:
			result+=' '*DPPreferences['NB_CHAR_PER_INDENT']
			for line in block:
				result+=u' '.join(line)+u'\n'
		return result
		
class DPStatisticsDialog(QtGui.QDialog):
	def __init__(self,textedit=False,text=False,*args,**kargs):
		"""
		This is a display dialog window to show the statistics of the text.
		- textedit: a TETextEdit instance the text has to be displayed
		- text: if there is no textedit, then if will display the string 
			contained in text.
		- *args,**kargs: argument putted in the constructor of QDialog.
		"""
		QtGui.QDialog.__init__(self,*args,**kargs)
		assert textedit or text, "Either <textedit> or <text> should contain something"
		
		button_quit 		= QtGui.QPushButton('Quit')
		button_refresh	 	= QtGui.QPushButton('Refresh')
		self.textedit=textedit
		
		self.info =   [	'nb_pages', 
					'nb_blocs', 
					'nb_lines',
					'nb_words',
					'nb_chars_without_spaces', 
					'nb_chars_with_spaces'
					]
		self.titles = [	'Number of pages', 
					'Number of paragraphs', 
					'Number of lines',
					'Number of words', 
					'Number of chars (without spaces)',
					'Number of chars (with spaces)',
					]
				
		self.table = QtGui.QTableWidget(len(self.info), 2, parent =self)
		self.table.verticalHeader().setVisible(False)
		self.table.horizontalHeader().setVisible(False)
		if not self.textedit:
			self.refresh(text)
		else :
			self.refresh()
		
		
		main_layout=QtGui.QVBoxLayout()
		main_layout.addWidget(self.table	)
		main_layout.addWidget(button_quit	)
		main_layout.addWidget(button_refresh)
		
		self.connect(button_quit	, QtCore.SIGNAL('clicked()'), self.accept)
		self.connect(button_refresh , QtCore.SIGNAL('clicked()'), self.refresh)
		self.setLayout(main_layout)
		
		if not self.textedit:
			button_refresh.setEnabled(False)
			
			
		margins = self.contentsMargins()
		w = self.table.horizontalHeader().length()
		w += margins.left() + margins.right()
		QtGui.QDialog.show(self)
		size = self.size()
		size.setWidth (w)
		self.resize(size)		
		# self.adjustSize()		
		
	
	def refresh(self,text=False):
		"""
		Slot called to refresh the information of the table according to the text contained 
		in self.textedit or in the parameter text.
		- text: if not known, will display this information rather than the one contained in
			self.textedit
		Either self.textedit or text should not be False.
		"""
		assert self.textedit or text, "Either <textedit> or <text> should contain something"
		if text:
			res = DPStatistics.stats(text,self.info)
		else :
			res = DPStatistics.stats(unicode(self.textedit.toPlainText()),self.info)
			
		
		for i,(self.title, val) in enumerate(zip(self.titles,res)):
			self.table.setItem(i,0,QtGui.QTableWidgetItem(self.title))		
			self.table.setItem(i,1,QtGui.QTableWidgetItem(str(val)))
		self.table.resizeColumnsToContents()
		
		
if __name__ == '__main__':
	import codecs
	import sys
	
	path = r"C:\Users\Renaud\Documents\Programmation\Python\AthenaWriterTest\Test.athw"
	# file = open(path,'r')
	file = codecs.open(path, encoding='utf-8', mode='r')
	text = file.read()
	file.close()
	# print TSTextStatistics.shape_book(text).encode('ascii','replace')
	
	app = QtGui.QApplication(sys.argv)
	writerText = DSDialogManager(text=text,parent=None)
	writerText.show()
	if len(sys.argv)>1:
		filepath=sys.argv[1]
		writerText.SLOT_actionFileOpen(filepath=filepath)
	
	sys.exit(app.exec_())
	
	
