"""
TODO :

remove the ugly self.__dict__ !!
make a better variable change by looking the type

- default_author

"""

from PyQt5 import QtGui, QtCore, QtWidgets

import xml.dom.minidom as XML
from TextLanguages.TextLanguages import TLChoice
from ConstantsManager.ConstantsManager import CMConstantsManager
from TextLanguages.TextLanguages import TLChoice
from TextLanguages.TextLanguagesPreferences import TLPreferences
from .DocPropertiesPreferences import DPPreferences

# These functions are added to the XML.Node structure :
def getFirstElementsByTagName(node,name):
	# allows from a name to have the first element with a specific tag name
	node=node.firstChild
	while node!=None:
		if node.nodeType==XML.Node.ELEMENT_NODE and node.tagName==name:
			return node
		node=node.nextSibling
	return None



class DPMetaData(CMConstantsManager):
	start_defaults 	= dict(
		author = (str,DPPreferences['DEFAULT_AUTHOR']),
		date = (str,''),
		language = (TLChoice,TLPreferences['DFT_WRITING_LANGUAGE']),
		version = (float,-1),
		lastpos = (int,-1),
		profile = (int,0),
		athw_version = (str,"Unknown"),
		)

	keys_protected = {'lastpos','profile'}

	constrains = dict(
		version = {'min':-1},
		lastpos = {'min':-1},
		)

	@staticmethod
	def init_from_xml_string(xml_string=None):
		"""Class that will interpret the text in order to get the informations"""
		dom = XML.parseString(xml_string.encode('utf-8'))

		node_structure  = getFirstElementsByTagName(dom ,'structure')

		element_dict = {}
		res = DPMetaData()
		for element,v in list(res.start_defaults.items()):
			type_ = v[0]
			node	= getFirstElementsByTagName(node_structure,element)
			if node!=None and node.hasChildNodes():
				try :
					information = type_(node.childNodes[0].toxml())
					element_dict[element]=information
				except ValueError:
					print("Warning, metadata <"+element+\
							"> do not fit the format")
		res.update(element_dict,protected=False)
		return res

	def toxml(self):
		doc = XML.Document()
		structure_node=doc.createElement('structure')

		for k in self.keys(skip_same_as_dft=False,protected=False):
			node=doc.createElement(k)
			text_node = doc.createTextNode(str(self[k]))
			node.appendChild(text_node)
			structure_node.appendChild(node)

		doc.appendChild(structure_node)

		return self.toPrettyWithText(doc)

	def toPrettyWithText(self,xml_node):
		"""
		 allows to have a string representation of the XML structure that has the text node
		 just between the including nodes.
		 Example : If we have text_xlm_element=='text', before we had
		 >>> ...
		 >>> <text>
		 >>> 		SomeText
		 >>> </text>
		 >>> ...
		 And with this function :
		 >>> ...
		 >>> <text>SomeText</text>
		 >>> ...
		"""
		indent='  '
		uglyXml = xml_node.toxml()
		prettyXml =''

		i=0
		for text_xlm_element in self.keys(protected=False) :
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






if __name__ == '__main__':
	import sys
	import os
	app = QtWidgets.QApplication(sys.argv)
	to_analyse="""<?xml version="1.0" ?>
					<structure>
					<author>Renovatio</author>
					<title>Renovatio</title>
					<version>1</version>
					</structure>"""
	print("type(to_analyse) : ", type(to_analyse))
	mtdt = MDMetaData()
	gui = MDMetaDataDialog(metadata=mtdt)
	gui.show()
	print("mtdt.toxml()  :  ",mtdt.toxml())
