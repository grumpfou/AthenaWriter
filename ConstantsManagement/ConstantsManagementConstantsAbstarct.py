

import sys
import os


# ############ IMPORTATION OF FMFileManagement ############
# try :
# 	# We try to see if it is already available
# 	from FileManagement.FileManagementFileConstants import FMFileConstants
# except ImportError:
# 	# Otherwise we try to see if it is not in the parent directory (but if 
# 	# is has been loaded before, it would not be reloaded anymore.
# 	import imp
# 		
# 	dir,f	= os.path.split(__file__)
# 	dir,f	= os.path.split(dir)
# 	
# 	import imp
# 		
# 	dir,f	= os.path.split(__file__)
# 	dir,f	= os.path.split(dir)
# 	dir 	= os.path.join(dir,'FileManagement')
# 
# 	foo = imp.find_module('FileManagementFileConstants', [dir])
# 	foo = imp.load_module('FileManagementFileConstants',*foo)
# 	FMFileConstants=foo.FMFileConstants	
# 	
# 	# sys.path.append(dir) # to be able to import TextFormat
# ############################################################
# 





class CMConstantsAbstarct:
	all_constants 		= { }
	all_sub_constants  	= { }	
	"""
	=== Writing a subclass ===
	To rewrite with the following format :
	self.all_constants= { constant_name : ( type, default_value ,decr) ,...}
	Descr is optional. If you want to have a list of things of a certain type :
	self.all_constants= { constant_name : ( [type], [default_values]) ,...}
	
	You can also implement some synonyms :
	self.all_synonyms= { synonym_name : correcponding_constant_name , 
						synonym_name  : another_synonym_name ,... }
	
	example:	
	>>> self.all_constants= {
	>>> 		"JUSTIFY" 	: ( bool   	, True  	, 'for justify' ),
	>>> 		"SIZE"		: ( int    	, 16 		, 'the font size' ),
	>>> 		"FONT"		: ( unicode , "Times" 	, 'the font name' ),
	>>> 		}
	>>> self.all_synonyms = { "FONT_NAME":"FONT" , "NAME_FONT" :"FONT_NAME"}
	
	
	=== Use of the subclass ===
	>>> Constants(**kargs)
	kargs has as keys it's keys the name of the constant and has the value the 
	value you want to overwrite/
	
	example:
	>>> Constants(JUSTIFY=False) # will replace the constant JUSTIFY as false
	"""
	
	def __init__(self,dict_overwrite=None,dict_constants=None,
			dict_sub_constants_container=None):
		abs_path_script_file,tmp= os.path.split(sys.argv[0])
		self.abs_path_script_file=abs_path_script_file
		
		self.constants		= {k:v[1] for k,v in self.all_constants.items()}
		self.sub_constants	=self.all_sub_constants.copy()
		if dict_sub_constants_container!=None:
			for k,v in dict_sub_constants_container.items():
				self.overwrite_sub_constants(k,v)
		if dict_constants!=None:
			for k,v in dict_constants.items():
				self.overwrite_constants(k,v)
		if dict_overwrite!=None:
			for k,v in dict_overwrite.items():
				self.__setitem__(k,v)
		

	def overwrite_sub_constants (self,k,v=None):
		"""
		Will overwrite the sub-constants with the information contained in the 
		arguments.
		k : dictionary or string
		v : None if k is a dictionary; the corresponding sub-constant of the 
				key k otherwise
		
		There is 2 way of using this method :
		- k is a dictionary with as keys the names of the sub-constant and as 
				values the corresponding sub-constants.
		- k is the name of one sub-constants and v if the corresponding 
				sub-constants.
		
		"""

		
		if type(k)==dict:
			for kk,vv in dict_sub_constants_container.items():
				self.overwrite_sub_constants(kk,vv)
		else:
			assert type(k)==str or type(k)==unicode , "k should be either a "+\
					"string or a dictionary"
			self.sub_constants[k] = v
			
	def overwrite_constants (self,k,v=None):
		"""
		Will overwrite the constants with the information contained in the 
		arguments.
		k : dictionary or string
		v : None if k is a dictionary; the corresponding value of the key k 
				otherwise
		
		There is 2 way of using this method :
		- k is a dictionary with as keys the names of the constant and as 
				values the values constants.
		- k is the name of one constants and v if the corresponding value.
		
		"""		
		if type(k)==dict:
			for kk,vv in dict_sub_constants_container.items():
				self.overwrite_sub_constants(kk,vv)
		else:
			assert type(k)==str or type(k)==unicode , "k should be either a "+\
					"string or a dictionary"
			self.constants[k] = CMConstantsAbstarct.set_type(
												self.all_constants[k][0],v)
			
			
	
	def __setitem__(self,key,value):
		if '.' in key :
			keys = key.split('.')
			cst 	= self.sub_constants[keys[0]]
			new_key = '.'.join(keys[1:])
			cst[new_key] = value
		else :
			if key in self.sub_constants.keys():
				raise KeyError('Should not take as key a sub-constant name.')
				# self.overwrite_sub_constants(key,value)
			elif key in self.constants.keys():
				self.overwrite_constants(key,value)
			else:
				raise KeyError('The key <'+key+'> is unknown')
	
	def __getitem__(self,key):
		if '.' in key :
			keys = key.split('.')
			cst 	= self.sub_constants[keys[0]]
			new_key = '.'.join(keys[1:])
			return cst[new_key] 
		else :
			if key in self.sub_constants.keys():
				return self.sub_constants[key]
			elif key in self.constants.keys():
				return self.constants[key]
			else:
				raise KeyError('The key <'+key+'> is unknown')


		
	
	def to_string(self,with_descr=True,comment_sign='#',skip_same_as_dft=False,
			pre=None):
		"""
		with_descr : will display the description
		comment_sign : the sign to put in front of the description
		skip_same_as_dft : if True, it will skip (as it is able to determine) 
			the values that are the same as the default one.
		pre : some text to put in front of the key (default, nothing)
		"""
		if pre==None: pre=u''
		res=u''
		# res += unicode(comment_sign*5+' Constant file '+comment_sign*5+'\n\n')
		# res += comment_sign*3+' Direct Constants  '+comment_sign*3+'\n\n'
		for k,v in self.constants.items():
			
			if (not skip_same_as_dft) or (v!=self.all_constants[k][1]):
				if with_descr and len(self.all_constants[k])>=3:
					res+=comment_sign+' '+self.all_constants[k][2]+'\n'
				if type(v)==list:
					res+=pre+k+' : '+' | '.join(str(v))+'\n\n'
				elif type(v)==dict:
					to_join = [' '.join([kk,vv]) for kk,vv in v.items()]
					res+=pre+k+' : '+' | '.join(to_join)+'\n\n'
				else:
					res+=pre+k+' : '+unicode(v)+'\n\n'
			
			if k=='FileManagement':
				raise BaseException('bug')
				
		for kk,vv in self.sub_constants.items():
			res += comment_sign*3+' Sub-constants : '+kk+' '+comment_sign*3
			res += '\n\n'
			
			if isinstance(vv,CMConstantsAbstarct):
				res += vv.to_string(
						with_descr=with_descr,
						comment_sign=comment_sign,
						skip_same_as_dft=skip_same_as_dft,
						pre=pre+kk+'.',
						)
				
			elif isinstance(vv,dict):
				for kkk,vvv in vv.items():
					res+=pre+kk+'.'+kkk+' : '+unicode(vvv)+'\n\n'
			else :
				print type(vv)
				print 'CAUTION'
				res+=pre+kk+' : '+unicode(vv)+'\n\n'
		
		print 'res : ',
		return res
		
	def to_dict(self,pre=None):
		"""
		Return a dict with all the constants and the sub-consants under the 
		form:
		{	'SUBCONT.CONST1' : (current_value,
							type,
							default_value,
							description),
			...	}
							
		"""
		if pre==None: pre=""
		
		res = {}		
		for k in self.all_constants.keys():
			res[pre+k] = tuple([self.constants[k]]+list(self.all_constants[k]))
		for k,v in self.sub_constants.items():
			res1 = (v).to_dict(pre = pre+k+'.')
			res = dict(res.items()+res1.items()) #concatenate the dict
		return res		

	def loadFile(self,file_manager,file_to_read=None):
		"""Load the constants from the file file_to_read. If file_to_read is 
		None, then it will take self.file_to_read if it exists.
		- file_manager : FMFileConstants instance
		"""
		if file_to_read==None:	
			file_to_read = self.file_to_read
			
		if file_to_read!=False:
			file_to_read = os.path.expanduser(file_to_read)
			if os.path.exists(file_to_read):
				self.file_to_read = file_to_read
				result_dictionary = file_manager.open(self.file_to_read)
				for k,v in result_dictionary.items():
					try:
						self.__setitem__(k,v)
					except KeyError,e:
						print "Config error",e
						
			else:
				print (file_to_read+' not found, taking the default options!')
				CMConstantsAbstarct.__init__(self)
				
		else:
			raise Exception('file_to_read was not specified')				
	
	def saveFile(self,file_manager,file_to_read=None):
		"""Save the constants in the file file_to_read. If file_to_read is 
		None, then it will take self.file_to_read if it exists.
		- file_manager : FMFileConstants instance		
		"""		
		if file_to_read==None:	
			file_to_read = self.file_to_read
		
		if file_to_read:
			file_manager.save(self.to_string(),file_to_read)
		else:
			raise Exception('file_to_read was not specified')
	
	
	@staticmethod
	def set_type(type_to_perform,value):
		# if we should create a list
		if type(type_to_perform)==list:
			return CMConstantsAbstarct.str_to_list(value,type_to_perform)
		
		# if we should create a dictionary
		elif type(type_to_perform)==dict:
			return CMConstantsAbstarct.str_to_dict(value,type_to_perform)
		
		# if we should create a boolean
		elif type_to_perform==bool:
			return CMConstantsAbstarct.str_to_bool(value)		
		
		# otherwise
		else :
			return type_to_perform(value)	
	
	
	
	@staticmethod
	def str_to_list(value,type_to_perform):
		"""if we should create a list"""
		type_to_perform=type_to_perform[0]
		if type(value)!=list:
			value=[value]
		return [CMConstantsAbstarct.set_type(type_to_perform,v) for v in value]

	@staticmethod
	def str_to_dict(value,type_to_perform):
		"""if we should create a dictionary"""
		res = {}
		type_to_perform_key		= type_to_perform.keys()[0]
		type_to_perform_value	= type_to_perform.values()[0]
		
		if type(value)==dict:
			return {
					CMConstantsAbstarct.set_type(type_to_perform_key,key) : \
					CMConstantsAbstarct.set_type(type_to_perform_value,val) \
					for key, val in value.items()
					}
		elif type(value)!=list:
			value=[value]
		for kv in value:
			list_words = kv.split(' ')
			key = CMConstantsAbstarct.set_type(type_to_perform_key ,
																list_words[0])
			val = CMConstantsAbstarct.set_type(type_to_perform_value, 
												' '.join(list_words[1:]))
			res[key]=val
		return res

	@staticmethod
	def str_to_bool(value):
		""" if we should create a boolean"""
		if type(value)==str or type(value)==unicode:
			if value.lower()=='true':
				return True
			elif value.lower()=='false' :
				return False
		else :
			return bool(int(value))			
	
	
		
if __name__ == '__main__':
	class CMConstantsTest0 ( CMConstantsAbstarct):
		all_constants = {'a':({int:bool},{1:True},'it is a'),'b':(bool,True,'it is b')}
		all_sub_constants  	= { }	
	# class CMConstantsTest1 ( CMConstantsAbstarct):
		# all_constants 		= {'A':(float,10,'it is A'),'B':(float,20,'it is B')}
		# all_sub_constants  	= { 'sub': CMConstantsTest0()}	
	
	# cst = CMConstantsTest1()
	cst = CMConstantsTest0()
	cst['b']=False
	cst['a']=["1 true","2 false","3 true"]
	print cst.to_string()
	
		