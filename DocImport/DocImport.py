from .DocImportPreferences import DIPreferences,DITestLibreOffice
from FileManagement.FileManagement import FMTextFileManagement
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
			self.raw_text = FMTextFileManagement.open(self.file)
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
		FMTextFileManagement.save(self.text,filepath)
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
