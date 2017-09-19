"""
This file will create the Manager which is basically a class that contains
constants. It also contains gui widget to interact with the ConstantsManager
"""


class CMConstantsManager (dict):
	# The dict conatining the defaults values:
	# (The available keys are determined by the keys of all_defaults)
	start_defaults 			= { } # {key : (type,value)}

	# The dict conatining the descriptions
	descriptions  	= { } # {key : description}

	# the order in which display the constants:
	keys_list				= []

	# For the gui interface, some keys that can not be changed
	keys_protected			= set()

	# Some constrained for the int or the float
	#
	#int : (min,max,interval)
	#float : (min,max,interval)
	constrains ={} #{key:{'min':foo1,'max':foo2}}

	def __init__(self,a=None):

		self.update({k:v[1] for k,v in list(self.start_defaults.items()) },
															protected=False)
		if a.__class__ == self.__class__ or type(a)==dict:
			self.update(a)
		elif a!=None:
			raise TypeError('The parameter "a" should be a dict like')

	@staticmethod
	def new_from_defaults(start_defaults,descriptions=None,keys_list=None,
														keys_protected=None):
		""" This function VERY strange allows to create a subclass of
		CMConstantsManager with the corresponding start_defaults, descriptions,
		etc.
		return the suclass, not the instance.
		"""
		for k,v in list(start_defaults.items()):
			if type(k)!=str: raise TypeError('Every key of start_defaults should be a str')
		for k,v in list(start_defaults.items()):
			if len(v)!=2 or type(v[0])!=type:
				start_defaults = {k:(v.__class__,v) for k,v in list(start_defaults.items())}
				break
		d = {'start_defaults':start_defaults}

		if descriptions != None : d['descriptions']=descriptions
		else: d['descriptions']={}
		if keys_list != None : d['keys_list']=keys_list
		else: d['keys_list']=[]
		if keys_protected != None : d['keys_protected']=keys_protected
		else: d['keys_protected']=set()
		sb = type('special', (CMConstantsManager,), d)
		return sb


	def __setitem__(self,k,v,protected=True):
		"""
		protected : if True, will not able the modification of a protected key
		"""
		if protected and k not in self.keys(protected=False):
			raise KeyError('The key '+k+' is unkown for '+str(self.__class__))
		elif protected and k in self.keys_protected:
			raise KeyError('The key '+k+' is protected for '+\
														str(self.__class__))
		vv = self.start_defaults[k][0](v)
		if k in list(self.constrains.keys()):
			assert issubclass( self.start_defaults[k][0],int) or \
								issubclass( self.start_defaults[k][0],float)
			if 'min' in self.constrains[k]:
				if vv<self.constrains[k]['min']:
					raise ValueError('The value for the key '+k+ 'should be '+\
						'higher than '+ str(self.constrains[k]['min']))
			if 'max' in self.constrains[k]:
				if vv>self.constrains[k]['max']:
					raise ValueError('The value for the key '+k+ 'should be '+\
						'lower than '+ str(self.constrains[k]['max']))
		return dict.__setitem__(self,k,vv)


	def update(self,a,protected=True,skip_key_error=False):
		"""
		protected : if True, will not able the modification of a protected key
		"""

		for k,v in list(a.items()):
			if skip_key_error:
				try:
					self.__setitem__(k,v,protected=protected)
				except KeyError:
					pass
			else:
				self.__setitem__(k,v,protected=protected)


	def keys(self,skip_same_as_dft=False, protected=True):
		"""
		protected : if True, will not able the add of a protected key
		"""
		result = self.keys_list[:]
		tmp = []
		for k in dict.keys(self):
			if not (k in self.keys_list):
				tmp.append(k)
		tmp.sort()
		result += tmp
		if skip_same_as_dft:
			result = [k for k in result if self[k]!=self.start_defaults[k][1]]
		if protected:
			result = [k for k in result if k not in self.keys_protected]
		return  result

	def items(self,skip_same_as_dft=False):
		return [(k,self[k]) for k in self.keys( skip_same_as_dft=
															skip_same_as_dft)]
	def copy(self,replace_defaults=False):
		"""
		- replace_defaults: if True, will replace the defaults in
			self.start_defaults by the current values.
		"""
		res = self.__class__(dict.copy(self))
		if replace_defaults:
			res.start_defaults = res.start_defaults.copy()
			for k,v in 	list(res.start_defaults.items()):
				res.start_defaults[k] = (v[0],self[k])
		return res

	######### Will be specified in every implementation of it
	# def to_string(self,with_descr=True,comment_sign='#',skip_same_as_dft=False,
	# 		pre=''):
	# 	"""
	# 	with_descr : will display the description
	# 	comment_sign : the sign to put in front of the description
	# 	skip_same_as_dft : if True, it will skip (as it is able to determine)
	# 		the values that are the same as the default one.
	# 	pre : some text to put in front of the key (default, nothing)
	# 	"""
	# 	res=u''
	# 	for k in self.keys():
	# 		v = self[k]
	# 		if (not skip_same_as_dft) or (v!=self.start_constants[k][1]):
	# 			if with_descr and self.descriptions.has_key(k):
	# 				res+=comment_sign+' '+self.descriptions[k]+'\n'
	# 			if type(v)==list:
	# 				res+=pre+k+' : '+' | '.join(str(v))+'\n\n'
	# 			elif type(v)==dict:
	# 				to_join = [' '.join([kk,vv]) for kk,vv in v.items()]
	# 				res+=pre+k+' : '+' | '.join(to_join)+'\n\n'
	# 			else:
	# 				res+=pre+k+' : '+unicode(v)+'\n\n'
	#
	# 	return res
	#
	# def to_python_string(self,with_descr=True,skip_same_as_dft=False,pre=''):
	# 	res=u''
	# 	for k in self.keys():
	# 		v = self[k]
	# 		if (not skip_same_as_dft) or (v!=self.start_constants[k][1]):
	# 			if with_descr and  self.descriptions.has_key(k):
	# 				res += '# '+self.descriptions[k]+'\n'
	#
	# 			if type(v)=='str':
	# 				vv = "'"+v.replace("'",r"\'")+"'"
	# 			if type(v)=='unicode':
	# 				vv = "u'"+v.replace("'",r"\'")+"'"
	# 			else:
	# 				vv =str(v)
	# 			kk = k.replace("'",r"\'")
	# 			res += pre+"['"+kk+"'] = "+vv+'\n\n'
	#
	# 	return res
	#
	# def to_xml_string(self,with_descr=True,skip_same_as_dft=False,pre=''):
	# 	raise NotImplementedError()
	# 	# TODO
	# 	res=u''
	# 	for k in self.keys():
	# 		v = self[k]
	# 		if (not skip_same_as_dft) or (v!=self.start_constants[k][1]):
	# 			if with_descr and  self.descriptions.has_key(k):
	# 				res += '# '+self.descriptions[k]+'\n'
	#
	# 			if type(v)==str:
	# 				vv = "'"+v.replace("'",r"\'")+"'"
	# 			if type(v)==unicode:
	# 				vv = "u'"+v.replace("'",r"\'")+"'"
	# 			else:
	# 				vv =str(v)
	# 			kk = k.replace("'",r"\'")
	# 			res += pre+"['"+kk+"'] = "+vv+'\n\n'
	#
	# 	return res


	##########################################################################
		# self.constants		= {k:v[1] for k,v in self.all_constants.items()}
		# self.sub_constants	=self.all_sub_constants.copy()
		# if dict_sub_constants_container!=None:
			# for k,v in dict_sub_constants_container.items():
				# self.overwrite_sub_constants(k,v)
		# if dict_constants!=None:
			# for k,v in dict_constants.items():
				# self.overwrite_constants(k,v)
		# if dict_overwrite!=None:
			# for k,v in dict_overwrite.items():
				# self.__setitem__(k,v)


	@staticmethod
	def set_type(type_to_perform,value):
		# if we should create a list
		if type(type_to_perform)==list:
			return CMConstantsManager.str_to_list(value,type_to_perform)

		# if we should create a dictionary
		elif type(type_to_perform)==dict:
			return CMConstantsManager.str_to_dict(value,type_to_perform)

		# if we should create a boolean
		elif type_to_perform==bool:
			return CMConstantsManager.str_to_bool(value)

		# otherwise
		else :
			return type_to_perform(value)



	@staticmethod
	def str_to_list(value,type_to_perform):
		"""if we should create a list"""
		type_to_perform=type_to_perform[0]
		if type(value)!=list:
			value=[value]
		return [CMConstantsManager.set_type(type_to_perform,v) for v in value]

	@staticmethod
	def str_to_dict(value,type_to_perform):
		"""if we should create a dictionary"""
		res = {}
		type_to_perform_key		= list(type_to_perform.keys())[0]
		type_to_perform_value	= list(type_to_perform.values())[0]
		if type(value)==str:
			value = eval(value)
		if type(value)==dict:
			return {
					CMConstantsManager.set_type(type_to_perform_key,key) : \
					CMConstantsManager.set_type(type_to_perform_value,val) \
					for key, val in list(value.items())
					}
		elif type(value)!=list:
			value=[value]
		for kv in value:
			list_words = kv.split(' ')

			key = CMConstantsManager.set_type(type_to_perform_key ,
																list_words[0])
			val = CMConstantsManager.set_type(type_to_perform_value,
												' '.join(list_words[1:]))
			res[key]=val
		return res

	@staticmethod
	def str_to_bool(value):
		""" if we should create a boolean"""
		if type(value)==str or type(value)==str:
			if value.lower()=='true':
				return True
			elif value.lower()=='false' :
				return False
		else :
			return bool(int(value))
