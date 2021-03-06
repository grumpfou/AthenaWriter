############################# LIBRARIES AVAILABLE #############################
import os,sys
file_dir = os.path.realpath(os.path.dirname(__file__))
p = os.path.join(file_dir,'../')
sys.path.append(p)
###############################################################################
from ConstantsManager.ConstantsManager import CMConstantsManager

from CommonObjects.CommonObjects import COContrainedDict



class TSStyleAttr (COContrainedDict):
	"""A class that will define in a proper way the acceptable attributes for
	the styles"""
	list_keys = ["char_style","font_size","font_name","alignment","font_color"]
	def __init__(self,a=None):
		if type(a)==list or type(a)==str:
			a = CMConstantsManager.str_to_dict(a,{str:str})
		COContrainedDict.__init__(self,a)


class TSPreferencesAbstarct (CMConstantsManager):
	start_defaults 	= dict(
		DEFAULT_STYLE	= (TSStyleAttr,
			TSStyleAttr({	"font_size":"medium",
							"font_name":"Times",
							"alignment":"justify"})),
		EMPHASIZE_STYLE	= (TSStyleAttr,
			TSStyleAttr({"char_style":"italic"})),
		HEADER1_STYLE 	= (TSStyleAttr,
			TSStyleAttr({	"char_style":"bold",
							"font_size":"xx-large",
							"alignment":"center"})),
		HEADER2_STYLE 	= (TSStyleAttr,
			TSStyleAttr({"char_style":"bold","font_size":"x-large"})),
		HEADER3_STYLE 	= (TSStyleAttr,
			TSStyleAttr({"char_style":"bold"})),
		CODE_STYLE 		= (TSStyleAttr,
			TSStyleAttr({	"font_name":"Courier"})),
		PHANTOM_STYLE 	= (TSStyleAttr,
			TSStyleAttr({"font_color":"gray"})),
		SEPARATOR_STYLE	= (TSStyleAttr,
			TSStyleAttr({"alignment":"center"})),
		IMAGE_STYLE		= (TSStyleAttr,
			TSStyleAttr({	"font_color":"red",
							"char_style":"bold",
							"font_size":"small",
							"alignment":"center"})),
		COLOR1_STYLE 	= (TSStyleAttr,
			TSStyleAttr({"font_color":"blue"})),
		COLOR2_STYLE 	= (TSStyleAttr,
			TSStyleAttr({"font_color":"red"})),
		COLOR3_STYLE 	= (TSStyleAttr,
			TSStyleAttr({"font_color":"green"})),
		SEPARATOR_MOTIF	= (str,"***"),

		)

	descriptions 	= dict(
		DEFAULT_STYLE	= "The style of the default style (for the different "+\
			"options see TEFormatClass description)",
		EMPHASIZE_STYLE	= "The style of the emphasize style (for the "+\
			"different options see TEFormatClass description)",
		HEADER1_STYLE 	= 'The style of the header1',
		HEADER2_STYLE 	= 'The style of the header2',
		HEADER3_STYLE 	= 'The style of the header3',
		CODE_STYLE 		= 'The style of the code block',
		PHANTOM_STYLE 	= 'The style of the code block',
		SEPARATOR_STYLE	= "The style of the separator (for the different"+\
			"options see TEFormatClass description)",
		IMAGE_STYLE		= "The style of the image block",
		COLOR1_STYLE 	= 'The style of the color1',
		COLOR2_STYLE 	= 'The style of the color2',
		COLOR3_STYLE 	= 'The style of the color3',
		SEPARATOR_MOTIF	= "The string that will represent the separators",


			)
TSPreferences=TSPreferencesAbstarct()






class TSError (BaseException):
	def __init__(self,raison,position=False):
		"""
		Special Error in TextEdit error.
		"""
		self.raison	= raison
		self.position	= position
		print(self)
	def __str__(self):
		res=""
		if self.position:
			res+="In position "+str(self.position)+": "

		res+=self.raison

		return res.encode('ascii','replace')
