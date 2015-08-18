
############ IMPORTATION OF CMConstantsAbstarct ############
try :
	# We try to see if it is already available
	from ConstantsManagement.ConstantsManagementConstantsAbstarct import CMConstantsAbstarct
except ImportError:
	# Otherwise we try to see if it is not in the parent directory (but if is has been loaded before,
	# it would not be reloaded anymore.
	import imp,os,sys
		
	dir,f	= os.path.split(__file__)
	dir,f	= os.path.split(dir)
	sys.path.append(dir) # to be able to import TextFormat
	dir 	= os.path.join(dir,'ConstantsManagement')

	foo = imp.find_module('ConstantsManagementConstantsAbstarct', [dir])
	foo = imp.load_module('ConstantsManagementConstantsAbstarct',*foo)
	CMConstantsAbstarct=foo.CMConstantsAbstarct
############################################################

from DialogValues.DialogValuesAdditionalTypes import DVContrainedDict



class TSStyleAttributes (DVContrainedDict):
	"""A class that will define in a proper way the acceptable attributes for 
	the styles"""
	list_keys = ["char_style","font_size","font_name","alignment","font_color"]
	def __init__(self,a=None):
		if type(a)==list or type(a)==unicode:
			a = CMConstantsAbstarct.str_to_dict(a,{unicode:unicode})
		DVContrainedDict.__init__(self,a)
		
class TSConstantsAbstract (CMConstantsAbstarct):
	all_constants=dict(	
				# EMPHASIZE_STYLE_OLD				= (unicode	,"italic"	, "The style of the emphasize file (for now only 'italic')"),
				DEFAULT_STYLE	= ( TSStyleAttributes,
						TSStyleAttributes({	"font_size":"20",
											"font_name":"Times",
											"alignment":"justify"
											}), 
						"The style of the default style (for the different "+\
								"options see TEFormatClass description)",
						),
									
				EMPHASIZE_STYLE	= (TSStyleAttributes,
						TSStyleAttributes({"char_style":"italic"}), 
						"The style of the emphasize style (for the "+\
							"different options see TEFormatClass description)",
						),
				
				HEADER1_STYLE = (TSStyleAttributes,
						TSStyleAttributes({	"char_style":"bold",
											"font_size":"30",
											"alignment":"center"
											}),
						'The style of the header1'
						),
						
				HEADER2_STYLE = (TSStyleAttributes,
						TSStyleAttributes({	"char_style":"bold",
											"font_size":"25"
											}),
						'The style of the header2'
						),
						
				HEADER3_STYLE = (TSStyleAttributes,
						TSStyleAttributes({	"char_style":"bold",
											"font_size":"20"
											}),
						'The style of the header3'
						),
						
				CODE_STYLE = (TSStyleAttributes,
						TSStyleAttributes({	"font_name":"Courier",
											"font_size":"20"
											}),
						'The style of the code block'
						),

				PHANTOM_STYLE = (TSStyleAttributes,
						TSStyleAttributes({	#"font_name":"Courier",
											"font_color":"gray",
											# "font_size":"10"
											}),
						'The style of the code block'
						),
				
				SEPARATOR_STYLE	= (TSStyleAttributes,
						TSStyleAttributes({"alignment":"center"}), 
						"The style of the separator (for the different"+\
						"options see TEFormatClass description)"
						),
						
						
				IMAGE_STYLE	= (TSStyleAttributes,
						TSStyleAttributes({	#"font_name":"Courier",
											"font_color":"red",
											"char_style":"bold",
											"font_size":"10",
											"alignment":"center"
											}),
						"The style of the image block"
						),					
				SEPARATOR_MOTIF	= (unicode,
						"***", 
						"The string that will represent the separators"
						),
						
				)
TSConstants= TSConstantsAbstract()

class TSError (BaseException):
	def __init__(self,raison,position=False):
		"""
		Special Error in TextEdit error.
		"""
		self.raison	= raison
		self.position	= position
		print self
	def __str__(self):
		res=""
		if self.position:
			res+="In position "+str(self.position)+": "
		
		res+=self.raison
		
		return res.encode('ascii','replace')
