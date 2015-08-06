"""
TODO :

remove the ugly self.__dict__ !!
make a better variable change by looking the type
"""

from PyQt4 import QtGui, QtCore

import xml.dom.minidom as XML
from MetaDataConstants import MDConstants

# These functions are added to the XML.Node structure :
def getFirstElementsByTagName(node,name):
	# allows from a name to have the first element with a specific tag name
	node=node.firstChild
	while node!=None:
		if node.nodeType==XML.Node.ELEMENT_NODE and node.tagName==name:
			return node
		node=node.nextSibling
	return None


class MDMetaData:
	element_list  = ['author','title','date' ,'language','version','lastpos']
	element_type  = [unicode ,unicode,unicode,unicode   ,float    ,int      ]
	element_modif = [True    ,True   ,True   ,True      ,True     ,False    ]
	@staticmethod
	def init_from_xml_string(xml_string=None):
		"""Class that will interpret the text in order to get the informations"""
		dom = XML.parseString(xml_string.encode('utf-8'))
		
		node_structure  = getFirstElementsByTagName(dom ,'structure')
		
		element_dict = {}
		zipp = zip(MDMetaData.element_list,MDMetaData.element_type)
		for element,type_ in zipp:
			node	= getFirstElementsByTagName(node_structure,element)
			information = None
			if node!=None and node.hasChildNodes():
				try : 
					information = type_(node.childNodes[0].toxml())
				except ValueError:
					print "Warning, metadata <"+element+\
							"> do not fit the format"
			element_dict[element]=information
		
		return MDMetaData(element_dict=element_dict)
		
		
	def __init__(self,element_dict=None):
		if element_dict==None: 
			element_dict={}
			if MDConstants["DEFAULT_AUTHOR"]!="":
				element_dict["author"]=MDConstants["DEFAULT_AUTHOR"]
			
		for k in self.element_list:
			if element_dict.has_key(k):
				self.__dict__[k]=element_dict[k]
			else:
				self.__dict__[k]=None
		
	def toxml(self):
		doc = XML.Document()
		structure_node=doc.createElement('structure')
		
		for k in self.element_list:
			if self.__dict__[k]!=None:
				node=doc.createElement(k)
				text_node = doc.createTextNode(unicode(self.__dict__[k]))
				node.appendChild(text_node)
				structure_node.appendChild(node)				

		doc.appendChild(structure_node)
			
		return self.toPrettyWithText(doc)
		
	def toPrettyWithText(self,xml_node):
		# allows to have a string representation of the XML structure that has the text node
		# just between the including nodes.
		# Example : If we have text_xlm_element=='text', before we had
		# >>> ...
		# >>> <text>
		# >>> 		SomeText
		# >>> </text>
		# >>> ...
		# And with this function :
		# >>> ...
		# >>> <text>SomeText</text>
		# >>> ...
		indent='  '
		uglyXml = xml_node.toxml()
		prettyXml =u''
		
		i=0
		for text_xlm_element in self.element_list :
			opening  = '<'+text_xlm_element+'>' 
			closing  = '</'+text_xlm_element+'>' 
			j=	uglyXml.find(opening)
			
			while j!=-1:
				# We add what was before the text node, in a pretty way
				prettyXml+=(uglyXml[i:j+1]).replace('><','>\n<')
				i = j+1
				j =	uglyXml.find(closing,i)
				assert j!=-1
				# We add the text node as it is
				prettyXml+=uglyXml[i:j+1]
				i = j+1
				j =	uglyXml.find(opening,i)
		# We add what remained of the XML in a pretty way
		prettyXml+=uglyXml[i:].replace('><','>\n<')
			
		return prettyXml
		
		
	def isEmpty(self):
		for k in self.element_list:
			if self.__dict__[k]!=None:
				return False
		return True
		
	def getDict(self):
		res={}
		for k in self.element_list:
			if self.__dict__[k] !=None:
				res[k]=self.__dict__[k]
		return res
		
		



class MDMetaDataDialog (MDMetaData,QtGui.QDialog):
	def __init__(self,metadata=None,*args,**kargs):
		QtGui.QDialog.__init__(self,*args,**kargs)
		if metadata==None:
			metadata=MDMetaData()
		self.metadata = metadata
		self.dict_choice={}
		layout_info=QtGui.QFormLayout()
		
		zipp = zip(self.metadata.element_list,self.metadata.element_modif)
		for k,modifable in zipp:
			if modifable:
				choice = QtGui.QLineEdit()
				if self.metadata.__dict__[k]!=None:
					choice.setText (unicode(self.metadata.__dict__[k]))
				self.dict_choice[k]=choice
				layout_info.addRow(k+':',choice)
			
		
		layout_button=QtGui.QHBoxLayout ()
		button_ok 		= QtGui.QPushButton("OK")
		button_cancel 	= QtGui.QPushButton("Cancel")
		layout_button.addWidget(button_ok)
		layout_button.addWidget(button_cancel)
			
	
		layout_main=QtGui.QVBoxLayout ()
		layout_main.addLayout(layout_info)
		layout_main.addLayout(layout_button)	
		
		self.setLayout(layout_main)
		self.connect(button_cancel, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("close()"))
		self.connect(button_ok 	  , QtCore.SIGNAL("clicked()"), self.generateMeta)
	
	def generateMeta(self):
		zipp = zip(	MDMetaData.element_list,
					MDMetaData.element_type,
					MDMetaData.element_modif,
					)		
		for k,type_,modifable in zipp:
			if modifable:
				try :
					v = type_(self.dict_choice[k].text())
				except  ValueError:
					v = ""
				if len(v)>0:
					self.metadata.__dict__[k]=v
				else:
					self.metadata.__dict__[k]=None
		self.close()
				
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	to_analyse="""<?xml version="1.0" ?>
					<structure>
					<author>Renovatio</author>
					<title>Renovatio</title>
					<version>1</version>
					</structure>"""
	print "type(to_analyse) : ", type(to_analyse)
	mtdt = MDMetaData()
	gui = MDMetaDataDialog(metadata=mtdt)
	gui.show()
	print "mtdt.toxml()  :  ",mtdt.toxml()