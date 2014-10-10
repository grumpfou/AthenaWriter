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
	op=dict(
		newline 			= '\n' ,
		start_file 			= ''   ,
		end_file 			= ''   ,
		start_line 			= '\t' ,
		end_line 			= ''   ,
		# start_emphasize 	= '*'  ,
		# end_emphasize 		= '*'  ,
		# separator	 		= '***' ,
		)
	def __init__(self,format_manager):
		"""
		format_manager : the module of TEFormats
		"""
		self.format_manager=format_manager
		self.text = False
	
	def export(self,textedit=None,xml_string=None,**options):
		"""
		textedit : the TETextEdit instance.
		xml_string : the unicode string representing the xml file
			Note : either textedit and xml_string should not be None
		options : dict that overwrite the self.op			
		"""
		assert textedit!=None or xml_string!=None, \
							"either textedit and xml_string should not be None"
		
		op=self.op.copy()
		for k,v in options.items() : op[k]=v
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
		# text=text.replace('<'+self.format_manager.TEFormatEmphasize.xmlMark+'>'	,op['start_emphasize']	)
		# text=text.replace('</'+self.format_manager.TEFormatEmphasize.xmlMark+'>'	,op['end_emphasize']	)
		# text=text.replace('<'+self.format_manager.TEFormatSeparator.xmlMark+'/>'	,op['separator']	)
		text=op['start_line']+text.replace('\n',op['end_line']+op['newline']+op['start_line'])+op['end_line']
		text=op['start_file']+text+op['end_file']
		
		self.text=text
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
		
		
		
class FEExportTxt(FEExportGeneral):
	extension='txt'
	op=dict(
		newline 			= '\n'	,
		start_file 			= ''   	,
		end_file 			= ''   	,
		start_line 			= '\t' 	,
		end_line 			= ''   	,
		# start_emphasize 	= '*'  	,
		# end_emphasize 		= '*'  	,
		# separator	 		= '***' ,
		)

class FEExportHtml(FEExportGeneral):
	extension='html'
	op=dict(
		newline 			= '\n'	,
		start_file 			= ''   	,
		end_file 			= '</body>'	,
		start_line 			= '<p>\t' 	,
		end_line 			= '</p>'   	,
		# start_emphasize 	= '<i>'  	,
		# end_emphasize 		= '</i>'  	,
		# separator	 		= '<h2><center>***</center></h2>' ,
		)
		
	def export(self,textedit=None,xml_string=None,title=None,author=None,**kargs):
		pre='<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n<head>\n'
		
		if title!=None:
			pre += '  <title>'+title+ '</title>  \n'
		pre+='  <style type="text/css">\np\n{\ntext-indent:50px;\n} </style>\n  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n'
		
		if author!=None:
			  pre+='  <meta name="Author" content="' +author+'"/>\n'
		pre+='</head>\n<body>\n'
		if title!=None:
			pre += '  <h1>'+title+ '</h1>\n'
		
		return FEExportGeneral.export(self,textedit=textedit,xml_string=xml_string,start_file=pre)


class FEExportLaTeX(FEExportGeneral):
	extension='tex'
	op=dict(
		newline 			= '\n\n'	,
		start_file 			= ''   	,
		end_file 			= r'\end{document}',
		start_line 			= '' 	,
		end_line 			= ''   	,
		# start_emphasize 	= r'\startemph{}'  	,
		# end_emphasize 		= r'\endemph{}'  	,
		# separator 			= '\\begin{center}\n***\n\\end{center}'  	,
		)
		
	def export(self,textedit=None,xml_string=None,title=None,author=None,head=False,**kargs):
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
		if head :
			pre += 	"\\usepackage{fancyhdr}"+"\n"+\
					"\pagestyle{fancy}"+"\n"+\
					"\lhead{\textsc{"
			if title!=None:
				pre +=title
			pre += r"}}\cfoot{\thepage}\rhead{\textsc{"
			if author!=None:
				pre+=author
			pre += "}}\n"
		
		pre+=r"\begin{document}"+"\n"
		
		if title!=None:
			pre += r'\title{'+title+'}\n'
			pre += r'\date{}'+'\n'
			
		if author!=None:
			  pre+=r'\author{'+author+'}\n'
		# if title!=None or author!=None:
		if title!=None :
			pre += r'\maketitle'+'\n'
		text = FEExportGeneral.export(self,textedit=textedit,xml_string=xml_string,start_file=pre,end_file="",**kargs)
		
		#emph is a little bit complicated, it has to be done at every line:
		# it0 = 0
		# it1 = text.find(self.op['start_emphasize'])
		# newtext=""
		# while it1>=0:
		# 	newtext+=text[it0:it1]
		# 	it0 = text.find(self.op['end_emphasize'],it1)
		# 	to_replace = text[it1:it0]
		# 	to_replace=to_replace.replace('\n\n','}\n\n\\emph{')
		# 	newtext+=to_replace
		# 	it1 = text.find(self.op['start_emphasize'],it0)
		# 	
		# text=newtext+text[it0:]
		# 	
		# text=text.replace(self.op['start_emphasize'],r'\emph{'	)
		# text=text.replace(self.op['end_emphasize'],'}'	)
		text+=self.op['end_file']
		text = text.replace(u'\u00A0','~')
		
		self.text=text
		return self.text


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
	
	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		commandline = FEConstants['PDFLATEX_COMMAND']+' -output-directory '+\
			dirpath_inter+' '+filepath_inter
		return commandline
				
class FEExportEpub(FEExportExternal):
	extension='epub'
	intermediate_export_class =  FEExportHtml
	
	def get_command_line(self,filepath_inter,dirpath_inter,filepath_final):
		print 'filepath_inter : ',filepath_inter
		commandline = FEConstants['EBOOKCONVERT_COMMAND']+' '+\
			filepath_inter+' '+filepath_final
		return commandline
		
		
FEList = [FEExportTxt,FEExportHtml,FEExportLaTeX,FEExportPdf,FEExportEpub]