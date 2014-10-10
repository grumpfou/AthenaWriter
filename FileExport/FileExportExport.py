import os.path
import os
from FileExportConstants import FEConstants

############ IMPORTATION OF FMFileManagement ############
try :
	# We try to see if it is already available
	from FileManagement.FileManagement import FMFileManagement
except ImportError:
	# Otherwise we try to see if it is not in the parent directory (but if is has been loaded before,
	# it would not be reloaded anymore.
	import imp

	dir,f	= os.path.split(__file__)
	dir	= os.path.join(dir,'..')
	dir	= os.path.join(dir,'FileManagement')
	foo = imp.find_module('FileManagement', [dir])
	foo = imp.load_module('FileManagement',*foo)
	FMFileManagement=foo.FMFileManagement
############################################################

############ IMPORTATION OF TextFormats ############
try :
	# We try to see if it is already available
	from TextFormats.TextFormats import *
except ImportError:
	# Otherwise we try to see if it is not in the parent directory (but if is has been loaded before,
	# it would not be reloaded anymore.
	import imp,sys

	dir,f	= os.path.split(__file__)
	dir	= os.path.join(dir,'..')
	dir	= os.path.join(dir,'TextFormats')
	sys.path.append(dir)
	#	from TextFormats.TextFormats import *
	foo = imp.find_module('TextFormats', [dir])
	TextFormats = imp.load_module('TextFormats',*foo)
############################################################

dict_add = lambda A,B : dict(A.items()+B.items())

class FEExportGeneral:
	""" Class to reimplement for all the exportations
		options :
			- newline 			= '\n' : the string that determine the new lines.
			- start_file 		= ''   : the string to put at the beginning of each the line.
			- end_file 			= ''   : the string to put at the end of each the line.
			- start_line 		= '\t' : the string to put at the beginning of each the line.
			- end_line 			= ''   : the string to put at the end of each the line.
			- start_emphasize 	= '*'  : the string to put at the beginning of an emphasize fragment.
			- end_emphasize 	= '*'  : the string to put at the end of each an emphasize fragment.
	"""
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
	
	document_options=dict(
		title 	= (unicode,"","Title of the story"),
		author 	= (unicode,"","Author of the story"),
		version = (unicode,"","Version of the story"),
		)
	
	def __init__(self,format_manager):
		"""
		format_manager : the module of TEFormats
		"""
		self.format_manager=format_manager
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
		
		if textedit!=None:
			text = textedit.toXml()	
		else : 
			text = xml_string
			
		for format in self.format_manager.listCharFormat + \
										self.format_manager.listBlockFormat:
			if isinstance(format,TFFormatClassSeparator):
				marks = format.exportDict.get(self.extension,None)
				if marks==None : start_mark=''
				else:start_mark=marks[0]
				text=text.replace('<'+format.xmlMark+'/>',start_mark
					)
			else:
				marks = format.exportDict.get(self.extension,None)
				print 'marks : ',marks
				if marks==None : 
					start_mark=''
					end_mark=''
				else: start_mark , end_mark = marks
				text=text.replace('<'+format.xmlMark+'>',start_mark)
				text=text.replace('</'+format.xmlMark+'>',end_mark)
		# text=text.replace('<'+self.format_manager.TEFormatEmphasize.xmlMark+'>'	,format_options['start_emphasize']	)
		# text=text.replace('</'+self.format_manager.TEFormatEmphasize.xmlMark+'>'	,format_options['end_emphasize']	)
		# text=text.replace('<'+self.format_manager.TEFormatSeparator.xmlMark+'/>'	,format_options['separator']	)
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
		doc_op = self.get_doc_opt(**options)
		
		start_file = ""
		if doc_op['title'] != "":
			start_file += doc_op['title'].upper()+'\n\n'
		if doc_op['author'] != "":
			start_file += 'By '+doc_op['author']+'\n\n'
		if doc_op['version'] != "":
			start_file += 'version '+doc_op['version']+'\n\n'
		
		self.export_text_core(textedit=textedit,xml_string=xml_string,**options)
		self.text=start_file+self.text
		return self.text
		
	def export_file(self,filepath=None,default_saving_site=None,parent=None):
		"""
		- filepath : the path to the destination file (will change the extension if necessary
			if None, will ask where to save it.
		- default_saving_site : in case if filepath is None, it will be the default place where 
			to put start the file window.
		- parent : in case if filepath is None, it will be the parent for the file window.
		"""
		assert self.text, 'Yous should run self.export() before'
		if filepath==None:#OLD!!!
			print "default_saving_site  :  ",default_saving_site#OLD!!!
			res1 = FMFileManagement.save_gui(unicode(self.text),default_saving_site,#OLD!!!
						extension=self.extension,parent=parent)
		else:
			filepath,e = os.path.splitext(filepath)
			filepath += '.' + self.extension
			res1 = FMFileManagement.save(unicode(self.text),filepath=filepath)
		return res1
		
		
	
	def get_doc_opt(self,**options):
		"""
		Will return a dictionnary containg the document options with the good 
		format. 
		Note: the resulting dictionnary will have the form of
		{ key : value }  which is not the same as self.document_options.
		"""
		doc_op = {k:v[1] for k,v in self.document_options.items()}
		
		for k,v in options.items() : 
			if k in self.document_options.keys() :
				doc_op[k]=self.document_options[k][0](v)
		
		return doc_op
		
		
class FEExportTxt(FEExportGeneral):
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

class FEExportHtml(FEExportGeneral):
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
		
		
		doc_op = self.get_doc_opt(**options)
		
		head = '<?xml version="1.0" encoding="UTF-8"?>\n'+\
				'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"'+\
				' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'+\
				'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n'+\
				'<head>\n'
		start = ""		
		if doc_op['title'] != "":
			head += '  <title>'+doc_op['title']+ '</title>  \n'
			start += '<h1>'+doc_op['title']+ '</h1>\n'
		head +='  <style type="text/css">\n'+\
				'p\n{\ntext-indent:50px;\n'+\
				'} </style>\n'+\
				'  <meta http-equiv="Content-Type" content="text/html; '+\
				'charset=UTF-8" />\n'
		if doc_op['author'] != "":
			head += '  <meta name="Author" content="' +doc_op['author']+\
																		'"/>\n'
			start += '<p>'+doc_op['author']+ '</p>\n'
		head +='</head>\n<body>\n'
		
		self.export_text_core(textedit=textedit,xml_string=xml_string,**options)
		self.text=head+start+self.text+'</body>'
		return self.text

class FEExportLaTeX(FEExportGeneral):
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
		
	document_options = dict_add(FEExportGeneral.document_options,dict(
		head 	= (bool,False,"Head on top of each page of the file"),
		date 	= (bool,False,"Will display the date in the file"),
		))
		
	def export(self,textedit=None,xml_string=None,**options):
		doc_op = self.get_doc_opt(**options)
		
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
		if doc_op['head'] :
			pre += 	r"\usepackage{fancyhdr}"+"\n"+\
					r"\pagestyle{fancy}"+"\n"+\
					r"\lhead{\textsc{"
			if doc_op['title']!=None:
				pre +=doc_op['title']
			pre += r"}}\cfoot{\thepage}\rhead{\textsc{"
			if doc_op['author']!=None:
				pre+=doc_op['author']
			pre += "}}\n"
		
		pre+=r"\begin{document}"+"\n"
		
		if doc_op['title']!="":
			pre += r'\title{'+doc_op['title']+'}\n'
			if not doc_op['date']:
				pre += r'\date{}'+'\n'
			
		if doc_op['author']!="":
			  pre+=r'\author{'+doc_op['author']+'}\n'
		# if title!=None or author!=None:
		if doc_op['title']!="" :
			pre += r'\maketitle'+'\n'
		
		self.export_text_core(textedit=textedit,xml_string=xml_string,**options)
		
		# replace the unbreakable spaces
		self.text = self.text.replace(u'\u00A0','~')
		
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


class FEExportExternal (FEExportGeneral):
	"""Abstract class used to export via an external software"""
	extension = None
	intermediate_export_class = None
	
	def export(self,*args,**kargs):
		intermediate = self.intermediate_export_class(self.format_manager)
		text = intermediate.export(*args,**kargs)
		self.text = text
		return text
		
	def export_file_intermediate(self,filepath=None,default_saving_site=None,
															parent=None):
		"""Returns (filepath_inter,dirpath_inter,filepath_final)"""
		if filepath==None:
			filepath_final = FMFileManagement.save_gui(unicode(self.text),
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
			FMFileManagement.save(unicode(self.text),filepath=filepath_inter)
			
		return filepath_inter,dirpath_inter,filepath_final
	
	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		""" Its re-implementation should retrun something like :
			>>> FEConstants['PDFLATEX_COMMAND']+' -output-directory '+\
			>>> dirpathtex+' '+filepathtex
		"""
		raise NotImplementedError()
		
	
	def export_file(self,filepath=None,default_saving_site=None,parent=None):
		"""
		Re-implementation of FEExportGeneral.export_file.
		- filepath : the math to the destination file (will change the 
			extension if necessary if None, will ask where to save it.
		- default_saving_site : in case if filepath is None, it will be the 
			default place where to put start the file window.
		- parent : in case if filepath is None, it will be the parent for the 
			file window.
		"""
		assert self.text, 'Yous should run self.export() before'
		filepath_inter , filepath_final , dirpath_inter = \
				self.export_file_intermediate(
				filepath=filepath,
				default_saving_site=default_saving_site,
				parent=parent)
				
		commandline = self.get_command_line(filepath_inter , filepath_final , \
																dirpath_inter)
		print "commandline", commandline
		res1 = os.system(commandline)
		if res1!=0:
			raise IOError('Problem during convertion of the file, is the '+\
				'exportation command correct ?')
		return filepath_final
		
		
class FEExportPdf(FEExportExternal):
	extension='pdf'
	intermediate_export_class =  FEExportLaTeX
	document_options = intermediate_export_class.document_options
	
	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		commandline = FEConstants['PDFLATEX_COMMAND']+' -halt-on-error '+\
			' -output-directory '+dirpath_inter+' '+filepath_inter
		return commandline
				
class FEExportEpub(FEExportExternal):
	extension='epub'
	intermediate_export_class =  FEExportHtml
	document_options = dict_add(intermediate_export_class.document_options,
		dict( cover_file = (unicode,"","The image that should represent "+\
			"cover of the file, if None, Calibre will generate its own")))
	
	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		print 'filepath_inter : ',filepath_inter
		# commandline = FEConstants['EBOOKCONVERT_COMMAND']+' -halt-on-error '+\
			# filepath_inter+' '+filepath_final
		commandline = FEConstants['EBOOKCONVERT_COMMAND']+' '+\
			filepath_inter+' '+filepath_final
		return commandline
		
		
FEList = [FEExportTxt,FEExportHtml,FEExportLaTeX,FEExportPdf,FEExportEpub]
FEDict = {format.extension:format for format in FEList} 
