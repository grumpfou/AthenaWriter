import subprocess
import os
import re
import codecs
from xml.dom.minidom import parseString

import socket
if socket.gethostname() == 'Revolution':
	lo=r'"C:\Program Files\LibreOffice 4.0\program\soffice.exe"'
else:
	lo='libreoffice'

class ATHW_odt2athw:
	def __init__(self,odt_file='./conver_test.odt'):
		self.odt_file = odt_file
		self.html_str  = False
		self.txt_str  = False
		self.athw_str = False
		
		
	def runAll(self):
		self.odt2html()
		self.html2txt()
		self.txt2athw()
		
	def odt2html(self,skip=False):
		args = '-headless -convert-to html -outdir'
		print 'self.odt_file : ',self.odt_file
		dir_file,tmp = os.path.split(self.odt_file)
		
		path,ext = os.path.splitext(self.odt_file)
		newfile = path+'.html'
		if not skip or not os.path.exists(newfile):
			to_call = lo + ' ' + args + ' ' +os.path.abspath(dir_file)+ ' '+ os.path.abspath(self.odt_file)
			print 'to_call : ',to_call
			os.system(to_call)
		else:
			print "Skip the creation of the file"
		
		# fi = codecs.open(newfile,'r',encoding='utf-8')
		fi = open(newfile,'r')
		
		try:
			self.html_str = fi.read()
		finally:
			fi.close()
	
	def html2txt(self):
		assert self.html_str,"You should run ATHW_odt2athw.odt2html before"
		
		dom = parseString(self.html_str)
		data = dom.getElementsByTagName('body')
		# tmp_txt_str = data[0].toprettyxml()
		tmp_txt_str = data[0].toxml()
		# tmp_txt_str =tmp_txt_str.replace('<li>',u'<li>\u2014')
		tmp_txt_str =tmp_txt_str.replace('</p>','</p>\n')
		
		# Remove all the HTML elements
		# self.txt_str = tmp_txt_str
		self.txt_str = ""
		it0 = 0
		it1 = tmp_txt_str.find('<')
		while it1>=0:
			self.txt_str+=tmp_txt_str[it0+1:it1]
			it0 = tmp_txt_str.find('>',it1)
			if it0<0:
				raise ValueError('Error in the html file, a element is not closed')
					
			it1 = tmp_txt_str.find('<',it0)
		
		# Clean the file (remove multiple spaces etc.)
		self.txt_str = re.sub("\n[\s]*",'\n',self.txt_str)
		if self.txt_str[0]=='\n':
			self.txt_str = self.txt_str[1:]
		self.txt_str = self.txt_str.replace(u'\n\u2014.',u'\n\u2014\u00A0')
		self.txt_str = self.txt_str.replace(u'&lt;',u'<')
		self.txt_str = self.txt_str.replace(u'&gt;',u'>')
		
	def html2athw(self):
		assert self.html_str,"You should run ATHW_odt2athw.odt2html before"
		
		tmp_txt_str = self.html_str.replace('</p>','</p>\n')

		dom = parseString(tmp_txt_str)
		
		css = dom.getElementsByTagName('style')[0]
		
		#to avoid the commentary nodes:
		css_text = '\n'.join([i.data for i in css.childNodes if i.nodeType == i.TEXT_NODE]) 
		css_list = css_text.split('\n')
		list_emphasize=[]
		for css_element in css_list:
			css_element=css_element.strip()
			if 'font-style:italic;' in css_element:
				it = css_element.find(' ')
				if it>=0:
					list_emphasize.append(css_element[1:it])
		print "list_emphasize : ", list_emphasize
		
		
		
		data = dom.getElementsByTagName('body')[0]
		
		def yield_element(node,list_nodes=None):
			if list_nodes==None: 
				list_nodes=[]
				
			for new_node in node.childNodes:
				yield_element(new_node,list_nodes)
			if node.nodeType != node.TEXT_NODE:
				list_nodes.append(node)
			return list_nodes
		
		# we replace the italics nodes with emphasize
		for element in yield_element(data):
			values = [attr.value for attr in element.attributes.values()]
			# print "values : ", values
			for emph in list_emphasize:
				if emph in values:
					# print "COUCOU"
					element.tagName='e'
					for key in element.attributes.keys():
						element.removeAttribute(key)


		tmp_athw_str = data.toxml()
		
		# Remove all the HTML elements
		self.athw_str = ""
		it0 = 0
		it1 = tmp_athw_str.find('<')
		while it1>=0:
			self.athw_str+=tmp_athw_str[it0+1:it1]
			it0 = tmp_athw_str.find('>',it1)
			if it0<0:
				raise ValueError('Error in the html file, a element is not closed')
			xml_element = tmp_athw_str[it1:it0+1]
			if xml_element in ['<e>','</e>']:
				self.athw_str+=tmp_athw_str[it1:it0+1]
			
			it1 = tmp_athw_str.find('<',it0)
		
		# Clean the file (remove multiple sapces etc.)
		self.athw_str = re.sub("\n[\s]*",'\n',self.athw_str)
		self.athw_str = self.athw_str.replace(u'</e>\n<e>','\n')
		self.athw_str = self.athw_str.replace(u'</e><e>','')
		self.athw_str = self.athw_str.replace(u'</e> <e>',' ')
		if self.athw_str[0]=='\n':
			self.athw_str = self.athw_str[1:]
		self.athw_str = self.athw_str.replace(u'\n\u2014.',u'\n\u2014\u00A0')
		self.athw_str = self.athw_str.replace(u'&lt;',u'<')
		self.athw_str = self.athw_str.replace(u'&gt;',u'>')
		
	def save_athw(self):
		assert self.athw_str,"You should run ATHW_odt2athw.html2athw before"
		path,ext = os.path.splitext(self.odt_file)
		fid = codecs.open(path+'.athw','w',encoding='utf8')
		try:
			fid.write(self.athw_str)
		finally:
			fid.close()
		
		
if __name__ == "__main__":
	converter = ATHW_odt2athw('./tests/Origine.doc')
	converter.odt2html(skip=True)	
	converter.html2athw()	
	converter.save_athw()	
	print converter.athw_str
