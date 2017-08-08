from .DocImportPreferences import DIPreferences,DITestLibreOffice
from FileManagement.FileManagement import FMFileManagement
from DocExport.DocExportPreferences import DEPreferences, DETestPandoc

from PyQt5 import QtGui, QtCore, QtWidgets
import subprocess
import os
import re
import codecs
import tempfile



class DIImportGeneral:
	extension=None
	def __init__(self,file=None,fromtext=None):
		"""
		A general class for importation (usually used with re-implementations)
		- file : the file to open with the text
		- fromtext: if file==None, we will take the string of these argument
			as the text to import.
		"""
		assert file!=None or fromtext!=None, 'either file or fromtext argument should not be None'
		if file!=None:
			self.file = file
			self.raw_text = FMFileManagement.open(self.file)
		else:
			self.file=None
			self.raw_text = fromtext
		self.text =False


	def import2xml(self):
		self.text = self.raw_text[:]
		return self.text

	def save_file(self,filepath=None,outdir=None):
		"""
		- filepath : the complete path where to save the file (with extension)
			Note: if filepath==None, it will take the self.file name as the path where
			to save the file.
			Note : if the DIImport instance was not created with a 'file' argument,
			this argument is mandatory.
		- outdir : it will take filemname (if filepath!=None, it will take it own) , and will use
			the outdir as directory where to save
		"""

		assert self.text,"You should run import2xml before"
		assert filepath!=None or self.file!=None,"Please indiquate the filepath"
		if self.file!=None and filepath==None:
			path,ext = os.path.splitext(self.file)
			filepath = path+'.athw'
		if outdir!=None:
			path,fi = os.path.split(self.file)
			filepath = os.path.join(outdir,fi)
		FMFileManagement.save(self.text,filepath)
		return filepath

	def skipLine(self,line_number):
		text_split = self.text.split('\n')
		result = text_split.pop(line_number)
		self.text = '\n'.join(text_split)
		return result


class DIImportMarkdown (DIImportGeneral):
	extension=['md','mkd']

	def import2xml(self):
		sp = self.raw_text.split('\n')
		sp = [s.strip() for s in sp]
		tmp_txt = '\n'.join(sp)
		tmp_txt = re.sub(r'^\*\*\*+$',r'<sep/>',tmp_txt,flags=re.MULTILINE)
		tmp_txt = re.sub(r'([^\*])(\*)([^\*]+)(\*)([^\*])', r'\1<e>\3</e>\5',
												tmp_txt)
		tmp_txt = re.sub(r'^#([^#\n]+)', r'<h1>\1</h1>\n\n', tmp_txt, flags=re.MULTILINE)
		tmp_txt = re.sub(r'^##([^#\n]+)', r'<h2>\1</h2>\n\n', tmp_txt, flags=re.MULTILINE)
		tmp_txt = re.sub(r'^###([^#\n]+)', r'<h3>\1</h3>\n\n', tmp_txt, flags=re.MULTILINE)
		tmp_txt = re.sub(r"!\[(.*)\][s]*\((.*)\)",r'\1\n\n<img>\2</img>\n\n',
												tmp_txt, flags=re.MULTILINE)
		tmp_txt = re.sub(r"([^\n])\n([^\[!\n#\*<])",r'\1 \2',tmp_txt)
		tmp_txt = re.sub(r"\n\n+",r'\n',tmp_txt)
		#


		# tmp_txt = re.sub(r"\n+",r'\n',tmp_txt)

		# # Clean the file (re
		# move multiple spaces etc.)
		# sp = tmp_txt.split('\n\n')
		# sp = [s.strip() for s in sp if s.strip()!=""]
		# tmp_txt = '\n'.join(sp)
		#
		#
		self.text = tmp_txt

		return self.text


class DIImportExternal (DIImportGeneral):
	extension = ['odt','docx','html','htm','txt']
	intermediate_import_class = DIImportMarkdown
	"""Importation that will use the markdown (via Pandoc) as an
	intermedite"""

	def __init__(self,file=None):
		"""
		A general class for importation (usually used with re-implementations)
		- file : the file to open with the text
		"""
		assert file!=None , 'file argument should not be None'
		self.file=file
		self.raw_text=False
		self.text =False


	def import2xml(self):
		file_inter 	= self.get_file_inter_name()
		cmd_line = self.get_command_line(file_inter)
		subprocess.run(cmd_line)

		importmkd = self.intermediate_import_class(file=file_inter)
		self.text = importmkd.import2xml()

		os.remove(file_inter)
		return self.text

	def get_file_inter_name(self):
		"""Returns the intermediate file name that will contain the intermediate
		document"""
		f = tempfile.NamedTemporaryFile(encoding='utf-8',mode='r',delete=False)
		f.close()
		return f.name

	def get_command_line(self,file_inter):
		return [DEPreferences['PANDOC_COMMAND'],'-o',file_inter,self.file]

class DIImportDoc(DIImportExternal):
	extension = ['doc']
	intermediate_import_class = DIImportExternal
	"""Will improt from doc to odt (via libreoffice) to markdown (via pandoc)
	then to xml"""

	def get_command_line(self,file_inter):
		"""Returns the command line that will be executed by the program"""
		d ,_ = os.path.split(file_inter)
		return [DIPreferences['LIBREOFFICE_COMMAND'],'--headless',
			'--convert-to', 'odt', '-outdir',d,self.file]

	def get_file_inter_name(self):
		"""Returns the intermediate file name that will contain the intermediate
		document"""
		d = DIImportExternal.get_file_inter_name(self)
		d,_ = os.path.split(d)
		f,_ = os.path.splitext(self.file)
		return 	os.path.join(d,f+'.odt')


### class DIImportHtml (DIImportGeneral):
### 	extension='html'
### 	def __init__(self,file=None,fromtext=None):
### 		"""
### 		A general class for importation (usually used with re-implementations)
### 		- file : the file to open with the text
### 		- fromtext: if file==None, we will take the string of these argument
### 		"""
### 		assert file!=None or fromtext!=None, 'either file or fromtext argument should not be None'
### 		if file!=None:
### 			self.file = file
### 			self.raw_text = FMFileManagement.open(self.file,with_codecs=False)
### 		else:
### 			self.file=None
### 			self.raw_text = fromtext
### 		self.text =False
###
### 	def import2xml(self,separator=None):
### 		tmp_txt_str = self.raw_text.replace('</p>','</p>\n')
### 		tmp_txt_str = tmp_txt_str.replace('</i>','</e>')
### 		tmp_txt_str = tmp_txt_str.replace('<i>','<e>')
### 		tmp_txt_str = tmp_txt_str.replace('</P>','</p>\n')
### 		tmp_txt_str = tmp_txt_str.replace('</I>','</e>')
### 		tmp_txt_str = tmp_txt_str.replace('<I>','<e>')
###
###
### 		dom = parseString(tmp_txt_str)
###
### 		css = dom.getElementsByTagName('style')[0]
###
### 		#to avoid the commentary nodes:
### 		css_text = '\n'.join([i.data for i in css.childNodes if i.nodeType == i.TEXT_NODE])
### 		css_list = css_text.split('\n')
### 		list_emphasize=[]
### 		for css_element in css_list:
### 			css_element=css_element.strip()
### 			if 'font-style:italic;' in css_element:
### 				it = css_element.find(' ')
### 				if it>=0:
### 					list_emphasize.append(css_element[1:it])
###
### 		data = dom.getElementsByTagName('body')[0]
###
### 		def yield_element(node,list_nodes=None):
### 			if list_nodes==None:
### 				list_nodes=[]
###
### 			for new_node in node.childNodes:
### 				yield_element(new_node,list_nodes)
### 			if node.nodeType != node.TEXT_NODE:
### 				list_nodes.append(node)
### 			return list_nodes
###
### 		# we replace the italics nodes with emphasize
### 		for element in yield_element(data):
### 			values = [attr.value for attr in element.attributes.values()]
### 			for emph in list_emphasize:
### 				if emph in values:
### 					element.tagName='e'
### 					for key in element.attributes.keys():
### 						element.removeAttribute(key)
###
###
### 		tmp_text = data.toxml()
###
### 		if separator!=None:
### 			tmp_text.replace(separator,'<sep/>')
###
### 		# Remove all the HTML elements (except the one of ATHW
### 		self.text = ""
### 		it0 = 0
### 		it1 = tmp_text.find('<')
### 		while it1>=0:
### 			self.text+=tmp_text[it0+1:it1]
### 			it0 = tmp_text.find('>',it1)
### 			if it0<0:
### 				raise ValueError('Error in the html file, a element is not closed')
### 			xml_element = tmp_text[it1:it0+1]
### 			if xml_element in ['<e>','</e>','<sep/>']:
### 				self.text+=tmp_text[it1:it0+1]
###
### 			it1 = tmp_text.find('<',it0)
###
### 		# Clean the file (remove multiple spaces etc.)
### 		self.text = re.sub("\n[\s]*",'\n',self.text)
### 		self.text = self.text.replace(u'</e>\n<e>','\n')
### 		self.text = self.text.replace(u'</e><e>','')
### 		self.text = self.text.replace(u'</e> <e>',' ')
### 		if self.text[0]=='\n':
### 			self.text = self.text[1:]
### 		self.text = self.text.replace(u'\n\u2014.',u'\n\u2014\u00A0')
### 		self.text = self.text.replace(u'&lt;',u'<')
### 		self.text = self.text.replace(u'&gt;',u'>')
###
### 		return self.text
###
###
###
### class DIImportOdt (DIImportGeneral):
### 	extension='odt'
### 	def __init__(self,file=None,fromtext=None):
### 		"""
### 		A general class for importation (usually used with re-implementations)
### 		- file : the file to open with the text
### 		- fromtext: if file==None, we will take the string of these argument
### 		"""
### 		assert file!=None , 'file argument should not be None'
### 		self.file=file
### 		self.raw_text=False
### 		self.text =False
###
###
###
### 	def import2xml(self):
### 		self.odt2html() #transform the odtfile into html
### 		import_html = DIImportHtml(fromtext=self.raw_text)
### 		self.text =  import_html.import2xml()
### 		return self.text
###
### 	def odt2html(self,skip=False):
### 		args = '-headless -convert-to html -outdir'
### 		dir_file,tmp = os.path.split(self.file)
###
### 		path,ext = os.path.splitext(self.file)
### 		newfile = path+'.html'
### 		if not skip or not os.path.exists(newfile):
### 			to_call = DIPreferences['LIBREOFFICE_COMMAND'] + ' ' + \
### 						args + ' ' +\
### 						os.path.abspath(dir_file)+ ' '+ \
### 						os.path.abspath(self.file)
### 			print 'to_call : ',to_call
### 			res = os.system(to_call)
### 			if res!=0:
### 				raise IOError('Problem during convertion of the file, is the LIBREOFFICE_COMMAND correct ?')
### 		else:
### 			print "Skip the creation of the file"
###
### 		self.raw_text = FMFileManagement.open(newfile,with_codecs=False)
###
###
### class DIImportDoc (DIImportOdt):
### 	extension='doc'
###
### class DIImportDocx (DIImportOdt):
###	extension='docx'
###
### class DIImportTxt (DIImportGeneral):
### 	extension='txt'
# class FIOdtToAthwGui (	FIOdtToAthw , QtWidgets.QDialog ):
	# def __init__(self,parent=None,odt_file=None,dft_opening_saving_site=None):
		# if odt_file==None:
			# if dft_opening_saving_site==None: dft_opening_saving_site='.'
			# dialog= QtWidgets.QFileDialog(parent)
			# filepath = dialog.	getOpenFileName(parent,"Select the .odt or .doc file to convert",
					# dft_opening_saving_site)
			# if filepath:
				# odt_file = unicode(filepath)
			# else:
				# False
		# FIOdtToAthw.__init__(self,odt_file=odt_file)
		# QtWidgets.QDialog.__init__(self,parent=parent)
		# #first line is the title
		# #skip lines
		# #sep symboles

# DIList = [DIImportOdt,DIImportHtml,DIImportDoc,DIImportDocx,DIImportTxt]
DIList = [DIImportMarkdown]
if DETestPandoc():
	DIList+=[DIImportExternal]

if DITestLibreOffice():

	DIList+=[DIImportDoc]

DIDict = {}
for a in DIList:
	if type(a.extension)==list:
		for e in a.extension:
			DIDict[e] = a
	else:
		DIDict[a.extension] = a
