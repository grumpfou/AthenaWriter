import os
from .DocExportPreferences import *
from TextStyles.TextStylesList import TSStyleClassSeparator,TSStylePhantom
from FileManagement.FileManagement import FMTextFileManagement
from pathlib import Path

def cm_add(A,start_defaults,descriptions={}):
	dict_add = lambda AA,BB : dict(list(AA.items())+list(BB.items()))
	res = CMConstantsManager.new_from_defaults(
		start_defaults = dict_add(A.start_defaults,start_defaults),
		descriptions = dict_add(A.descriptions,descriptions),
		)()
	return res


class DEExportGeneral:
	""" Class to reimplement for all the exportations
		options :
			- newline 			= '\n' : the string that determine the new lines.
			- start_line 		= '\t' : the string to put at the beginning of each the line.
			- end_line 			= ''   : the string to put at the end of each the line.
	"""
	name=None
	extension=None
	format_options=dict(
		newline 			= '\n' ,
		# start_file 			= ''   ,
		# end_file 			= ''   ,
		start_line 			= '\t' ,
		end_line 			= ''   ,
		# start_emphasize 	= '*'  ,
		# end_emphasize 		= '*'  ,
		# separator	 		= '***' ,
		)
	doc_opt = CMConstantsManager.new_from_defaults(
			start_defaults = dict(
				title 	= (str,""),
				author 	= (str,""),
				version = (str,""),
				phantom = (bool,True),
				),
			descriptions = dict(
				title 	= "Title of the story",
				author 	= "Author of the story",
				version = "Version of the story",
				phantom = "Export with phantom text",
				)
			)()


	def __init__(self,style_manager):
		"""
		style_manager : the module of TEFormats
		"""

		self.style_manager=style_manager
		self.text = False


	def export_text_core(self,textedit=None,xml_string=None,**options):
		"""
		This function will export the core of the text, it will return the
		text itself (without any header or termination). Usully it should be
		directly called by the export function.
		"""
		assert textedit!=None or xml_string!=None, \
							"either textedit and xml_string should not be None"

		format_options=self.format_options.copy()
		self.get_doc_opt(**options)

		if textedit!=None:
			text = textedit.toXml()
		else :
			text = xml_string

		for style in self.style_manager.listCharStyle + \
										self.style_manager.listBlockStyle:
			if isinstance(style,TSStyleClassSeparator):
				marks = style.exportDict.get(self.extension,None)
				if marks==None : start_mark=''
				else:start_mark=marks[0]
				text=text.replace('<'+style.xmlMark+'/>',start_mark
					)
			elif style==TSStylePhantom and not self.doc_opt['phantom']:
				start_mark = '<'+style.xmlMark+'>'
				end_mark = '</'+style.xmlMark+'>\n'
				i = text.find(start_mark)
				while i>=0:
					j = text.find(end_mark,i)
					assert j>=0, 'Error : a xml balise is not closed'
					j += len(end_mark)
					text = text[:i]+text[j:]
					i=text.find(start_mark,j)
			else:
				marks = style.exportDict.get(self.extension,None)
				if marks==None :
					start_mark=''
					end_mark=''
				else: start_mark , end_mark = marks
				text=text.replace('<'+style.xmlMark+'>',start_mark)
				text=text.replace('</'+style.xmlMark+'>',end_mark)
		# text=text.replace('<'+self.style_manager.TEFormatEmphasize.xmlMark+'>'	,format_options['start_emphasize']	)
		# text=text.replace('</'+self.style_manager.TEFormatEmphasize.xmlMark+'>'	,format_options['end_emphasize']	)
		# text=text.replace('<'+self.style_manager.TEFormatSeparator.xmlMark+'/>'	,format_options['separator']	)
		intreline = format_options['end_line'] + format_options['newline'] +\
												format_options['start_line']
		text = text.replace('\n',intreline)
		text = format_options['start_line']+text+format_options['end_line']

		self.text=text
		return self.text


	def export(self,textedit=None,xml_string=None,**options):
		"""
		textedit : the TETextEdit instance.
		xml_string : the unicode string representing the xml file
			Note : either textedit and xml_string should not be None
		options : dict that overwrite the self.format_options
		"""
		assert textedit!=None or xml_string!=None, \
							"either textedit and xml_string should not be None"
		self.get_doc_opt(**options)

		start_file = ""
		if self.doc_opt['title'] != "":
			start_file += self.doc_opt['title'].upper()+'\n\n'
		if self.doc_opt['author'] != "":
			start_file += 'By '+self.doc_opt['author']+'\n\n'
		if self.doc_opt['version'] != "":
			start_file += 'version '+self.doc_opt['version']+'\n\n'

		self.export_text_core(textedit=textedit,xml_string=xml_string,**options)
		self.text=start_file+self.text
		return self.text


	def export_file(self,filepath=None,default_saving_site=None,parent=None):
		"""
		- filepath : the path to the destination file (will change the
			extension if necessary if None, will ask where to save it.
		- default_saving_site : in case if filepath is None, it will be the
			default place where  to put start the file window.
		- parent : in case if filepath is None, it will be the parent for the
			file window.
		"""
		assert self.text, 'Yous should run self.export() before'
		if filepath==None:#OLD!!!
			res1 = FMTextFileManagement.save_gui(str(self.text),default_saving_site,#OLD!!!
						extension=self.extension,parent=parent)
		else:
			filepath,e = os.path.splitext(filepath)
			filepath += '.' + self.extension
			res1 = FMTextFileManagement.save(str(self.text),filepath=filepath)
		return res1



	def get_doc_opt(self,**options):
		"""
		Will return a dictionnary containg the document options with the good
		format.
		Note: the resulting dictionnary will have the form of
		{ key : value }  which is not the same as self.doc_opt_dft.
		"""

		for k,v in list(options.items()) :
			if k in list(self.doc_opt.keys()) :
				self.doc_opt[k]=v

		return self.doc_opt


class DEExportTxt(DEExportGeneral):
	name='Text'
	extension='txt'
	format_options=dict(
		newline 			= '\n'	,
		# start_file 			= ''   	,
		# end_file 			= ''   	,
		start_line 			= '\t' 	,
		end_line 			= ''   	,
		# start_emphasize 	= '*'  	,
		# end_emphasize 		= '*'  	,
		# separator	 		= '***' ,
		)

class DEExportHtml(DEExportGeneral):
	name='HTML'
	extension='html'
	format_options=dict(
		newline 			= '\n'	,
		# start_file 			= ''   	,
		# end_file 			= ''	,
		start_line 			= '<p>\t' 	,
		end_line 			= '</p>'   	,
		# start_emphasize 	= '<i>'  	,
		# end_emphasize 		= '</i>'  	,
		# separator	 		= '<h2><center>***</center></h2>' ,
		)

	#def export(self,textedit=None,xml_string=None,title=None,author=None,**kargs):
	#	pre = 	'<?xml version="1.0" encoding="UTF-8"?>\n'+\
	#			'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"'+\
	#			' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'+\
	#			'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n'+\
	#			'<head>\n'
	#
	#	if title!=None:
	#		pre += '  <title>'+title+ '</title>  \n'
	#	pre+='  <style type="text/css">\n'+\
	#			'p\n{\ntext-indent:50px;\n'+\
	#			'} </style>\n'+\
	#			'  <meta http-equiv="Content-Type" content="text/html; '+\
	#			'charset=UTF-8" />\n'
	#
	#	if author!=None:
	#		  pre+='  <meta name="Author" content="' +author+'"/>\n'
	#	pre+='</head>\n<body>\n'
	#	if title!=None:
	#		pre += '  <h1>'+title+ '</h1>\n'
	#
	#	res = pre
	#	res += FEExportGeneral.export(self,textedit=textedit,
	#													xml_string=xml_string)
	#	res += '</body>'
	#	return res

	def export(self,textedit=None,xml_string=None,**options):
		"""
		textedit : the TETextEdit instance.
		xml_string : the unicode string representing the xml file
			Note : either textedit and xml_string should not be None
		options : dict that overwrite the self.format_options
		"""
		assert textedit!=None or xml_string!=None, \
							"either textedit and xml_string should not be None"


		self.get_doc_opt(**options)

		head = '<?xml version="1.0" encoding="UTF-8"?>\n'+\
				'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"'+\
				' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'+\
				'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n'+\
				'<head>\n'
		start = ""
		if self.doc_opt['title'] != "":
			head += '  <title>'+self.doc_opt['title']+ '</title>  \n'
			start += '<h1>'+self.doc_opt['title']+ '</h1>\n'
		head +='  <style type="text/css">\n'+\
				'p\n{\ntext-indent:50px;\n'+\
				'} </style>\n'+\
				'  <meta http-equiv="Content-Type" content="text/html; '+\
				'charset=UTF-8" />\n'
		if self.doc_opt['author'] != "":
			head += '  <meta name="Author" content="' +self.doc_opt['author']+\
																		'"/>\n'
			start += '<p>'+self.doc_opt['author']+ '</p>\n'
		head +='</head>\n<body>\n'

		self.export_text_core(textedit=textedit,xml_string=xml_string,**options)
		self.text=head+start+self.text+'</body>'
		return self.text

class DEExportLaTeX(DEExportGeneral):
	name="LaTeX"
	extension='tex'
	format_options=dict(
		newline 			= '\n\n'	,
		# start_file 			= ''   	,
		# end_file 			= r'\end{document}',
		start_line 			= '' 	,
		end_line 			= ''   	,
		# start_emphasize 	= r'\startemph{}'  	,
		# end_emphasize 		= r'\endemph{}'  	,
		# separator 			= '\\begin{center}\n***\n\\end{center}'  	,
		)
	doc_opt = cm_add(DEExportGeneral.doc_opt,
			start_defaults= dict(
				head 	= (bool,False),
				date 	= (bool,False),
				),
			descriptions=dict(
				head 	= "Head on top of each page of the file",
				date 	= "Will display the date in the file",
				))

	def export(self,textedit=None,xml_string=None,**options):
		self.get_doc_opt(**options)

		# pre="\\documentclass[12pt]{article}\n\\usepackage{geometry}\n\\geometry{verbose,tmargin=3cm,bmargin=3cm,lmargin=2.5cm,rmargin=2.5cm}\n\\usepackage{graphicx}\n\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}\n\\renewcommand{\\baselinestretch}{1.5} \n "
		# pre=r"\documentclass[12pt]{article}\n\usepackage{geometry}\n\geometry{verbose,tmargin=3cm,bmargin=3cm,lmargin=2cm,rmargin=2cm}\n\usepackage{graphicx}\n\begin{document}\n "
		pre =  r"\documentclass[12pt]{article}"+"\n"
		pre += r"\usepackage{geometry}"+"\n"
		pre += r"\geometry{verbose,tmargin=3cm,bmargin=3cm,"+\
										r"lmargin=2.5cm,rmargin=2.5cm}"+"\n"
		pre += r"\usepackage{graphicx}"+"\n"
		pre += r"\usepackage[utf8]{inputenc}"+"\n"
		pre += r"\usepackage[T1]{fontenc}"+"\n"
		pre += r"\renewcommand{\baselinestretch}{1.5} "+"\n"
		if self.doc_opt['head'] :
			pre += 	r"\usepackage{fancyhdr}"+"\n"+\
					r"\pagestyle{fancy}"+"\n"+\
					r"\lhead{\textsc{"
			if self.doc_opt['title']!=None:
				pre +=self.doc_opt['title']
			pre += r"}}\cfoot{\thepage}\rhead{\textsc{"
			if self.doc_opt['author']!=None:
				pre+=self.doc_opt['author']
			pre += "}}\n"

		pre+=r"\begin{document}"+"\n"
		if self.doc_opt['title']!="" or self.doc_opt['version'] != "":
			pre += r'\title{'
			if self.doc_opt['title']!="":
				pre += self.doc_opt['title']
				if self.doc_opt['version'] != "":
					pre += r'\\ \tiny{Version '+self.doc_opt['version'] +'}'
			else:
				pre += 'tiny{Version '+self.doc_opt['version'] +'}'
			pre += '}\n'

			if not self.doc_opt['date']:
				pre += r'\date{}'+'\n'

		if self.doc_opt['author']!="":
			  pre+=r'\author{'+self.doc_opt['author']+'}\n'
		# if title!=None or author!=None:
		if self.doc_opt['title']!="" :
			pre += r'\maketitle'+'\n'

		self.export_text_core(textedit=textedit,xml_string=xml_string,**options)

		# replace the unbreakable spaces
		self.text = self.text.replace('\u00A0','~')

		self.text = pre+self.text+r'\end{document}'
		return self.text
		#emph is a little bit complicated, it has to be done at every line:
		# it0 = 0
		# it1 = text.find(self.format_options['start_emphasize'])
		# newtext=""
		# while it1>=0:
		# 	newtext+=text[it0:it1]
		# 	it0 = text.find(self.format_options['end_emphasize'],it1)
		# 	to_replace = text[it1:it0]
		# 	to_replace=to_replace.replace('\n\n','}\n\n\\emph{')
		# 	newtext+=to_replace
		# 	it1 = text.find(self.format_options['start_emphasize'],it0)
		#
		# text=newtext+text[it0:]
		#
		# text=text.replace(self.format_options['start_emphasize'],r'\emph{'	)
		# text=text.replace(self.format_options['end_emphasize'],'}'	)

class DEExportMarkdown(DEExportGeneral):
	name='Markdown'
	extension='mkd'
	format_options=dict(
		newline 			= '\n\n'	,
		# start_file 			= ''   	,
		# end_file 			= ''	,
		start_line 			= '' 	,
		end_line 			= ''   	,
		# start_emphasize 	= '*'  	,
		# end_emphasize 		= '*'  	,
		# separator	 		= '<h2><center>***</center></h2>' ,
		)

class DEExportExternal (DEExportGeneral):
	"""Abstract class used to export via an external software"""
	name=None
	extension = None
	intermediate_export_class = None

	def export(self,textedit=None,xml_string=None,**options):
		intermediate = self.intermediate_export_class(self.style_manager)
		text = intermediate.export(textedit=textedit,xml_string=xml_string,
																	**options)
		self.get_doc_opt(**options)
		self.text = text
		return text

	def export_file_intermediate(self,filepath=None,default_saving_site=None,
															parent=None):
		"""Returns (filepath_inter,dirpath_inter,filepath_final)"""
		if filepath==None:
			filepath_final = FMTextFileManagement.save_gui(str(self.text),
					default_saving_site,extension=self.extension,parent=parent)
			filepath_inter,e = os.path.splitext(filepath_final )
			dirpath_inter,e = os.path.split(filepath_final )
			filepath_inter = filepath_inter+ '.' +\
									self.intermediate_export_class.extension
			os.rename(filepath_final,filepath_inter) # THAT IS DIRTY
		else:
			filepath_final=filepath
			filepath_inter,e = os.path.splitext(filepath_final)
			dirpath_inter,e = os.path.split(filepath_inter)
			filepath_inter = filepath_inter+ '.' + \
									self.intermediate_export_class.extension
			FMTextFileManagement.save(str(self.text),filepath=filepath_inter)

		return filepath_inter,dirpath_inter,filepath_final

	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		""" Its re-implementation should retrun something like :
			>>> DEPreferences['PDFLATEX_COMMAND']+' -output-directory '+\
			>>> dirpathtex+' '+filepathtex
		"""
		raise NotImplementedError()


	def export_file(self,filepath=None,default_saving_site=None,parent=None):
		"""
		Re-implementation of DEExportGeneral.export_file.
		- filepath : the math to the destination file (will change the
			extension if necessary if None, will ask where to save it.
		- default_saving_site : in case if filepath is None, it will be the
			default place where to put start the file window.
		- parent : in case if filepath is None, it will be the parent for the
			file window.
		"""
		assert self.text, 'Yous should run self.export() before'
		filepath_inter , dirpath_inter, filepath_final   = \
				self.export_file_intermediate(
				filepath=filepath,
				default_saving_site=default_saving_site,
				parent=parent)

		print('filepath_inter : ',filepath_inter)
		print('dirpath_inter : ',dirpath_inter)
		print('filepath_final : ',filepath_final)
		commandline = self.get_command_line(filepath_inter , dirpath_inter,\
									filepath_final )
		print("commandline", commandline)
		old_d = os.getcwd()
		print('dirpath_inter : ',dirpath_inter)
		os.chdir(dirpath_inter) # change_dir for the local files
		res1 = os.system(commandline.encode('utf-8'))
		os.chdir(old_d)

		if res1!=0:
			raise IOError('Problem during convertion of the file, is the '+\
				'exportation command correct ?')
		return filepath_final


class DEExportPdf(DEExportExternal):
	name='PDF via LaTeX'
	extension='pdf'
	intermediate_export_class =  DEExportLaTeX
	doc_opt = cm_add(intermediate_export_class.doc_opt,
			start_defaults= dict(
				clean 	= (bool,False)
				),
			descriptions=dict(
				clean 	= "Clean intermediate files files at the end",
				))


	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		commandline = DEPreferences['PDFLATEX_COMMAND']+' -halt-on-error '+\
			' -output-directory '+dirpath_inter+' '+filepath_inter
		return commandline

	def export_file(self,filepath=None,*args,**kargs):
		res = DEExportExternal.export_file(self,filepath=filepath,*args,
																	**kargs)
		if self.doc_opt['clean']:
			ext_to_clean = ['tex','aux','log','dvi']
			f,tmp = os.path.splitext(filepath)
			for e in ext_to_clean:
				ff = f +'.'+e
				if os.path.exists(ff):
					os.remove(ff)
					print('Remove ',ff)
		return res

class DEExportEpub(DEExportExternal):
	name="EPUB via ebook-convert"
	extension='epub'
	intermediate_export_class =  DEExportHtml
	doc_opt = cm_add(intermediate_export_class.doc_opt,
			start_defaults= dict(
				cover_file 	= (Path,"")
				),
			descriptions=dict(
				cover_file 	= ("cover of the file, if None, Calibre will "
														"generate its own"),
				))



	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		print('filepath_inter : ',filepath_inter)
		commandline = DEPreferences['EBOOKCONVERT_COMMAND']+' '+\
			filepath_inter+' '+filepath_final
		return commandline

class DEExportPandocGeneral(DEExportExternal):
	name=None
	extension=None
	intermediate_export_class =  DEExportMarkdown

	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		print('filepath_inter : ',filepath_inter)
		commandline = DEPreferences['PANDOC_COMMAND']+' -o '+filepath_final+\
			' '+ filepath_inter
		return commandline

class DEExportPandocOdt(DEExportPandocGeneral):
	name="ODT via Pandoc"
	extension='odt'

class DEExportPandocDoc(DEExportPandocGeneral):
	name="DOC via Pandoc"
	extension='doc'

class DEExportPandocDocx(DEExportPandocGeneral):
	name="DOCX via Pandoc"
	extension='docx'

DEList = [
		DEExportTxt,
		DEExportHtml,
		DEExportLaTeX,
		DEExportMarkdown,
		]

if DETestPdfLatext():
	DEList += [DEExportPdf]

if DETestEbookConvert():
	DEList += [DEExportEpub]

if DETestPandoc():
	DEList += [
		DEExportPandocOdt,
		DEExportPandocDoc,
		DEExportPandocDocx,
		]
else:
	print("What the fuckEXP")

DEDict = {format.name:format for format in DEList}
