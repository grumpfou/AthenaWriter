class COError (StandardError):pass

class COContrainedDict(dict):
	list_keys = []
	def __init__(self,a=None):
		"""
		If a is a list of string: it will be the keys and all the values will 
		be initiated to None
		"""
		dict.__init__(self)
		if a ==None: a={}
		for k,v in a.items():
			self.__setitem__(k,v)
	
	def __setitem__(self,k,v,protected=True):
		if protected and k not in self.list_keys:
			raise KeyError('The key '+k+' is unkown for this ContrainedDict.')
		return dict.__setitem__(self,k,v)
	def __getitem__(self,k,protected=True):
		if protected and k not in self.list_keys:
			raise KeyError('The key '+k+' is unkown for this ContrainedDict.')
		return dict.__getitem__(self,k)
		
class COOrderedDict(dict):
	"""
	A dictionnary where the order in which we putted the items is remembered
	and displayed again in the same order
	"""
	def __init__(self,a=None):
		if a!=None:
			if type(a)==dict:
				self.list_keys = a.keys()
			elif type(a)==list:
				self.list_keys = [v[0] for v in a]
			dict.__init__(self,a)
		else:
			self.list_keys = []
			dict.__init__(self)
			
	def keys(self):
		return self.list_keys
		
	def items(self):
		for k in self.keys():
			yield k,self[k]
	
	def __setitem__(self,k,v):
		if k not in self.keys():
			self.list_keys.append(k)
		dict.__setitem__(self,k,v)
		
	def pop(self,k):
		res = dict.pop(self,k)
		self.list_keys.remove(k)
		return res
		
	

class COChoice:
	elements_list = [None]
	def __init__(self,value=None):
		"""
		A simple class where we have to chose an element in a given list.
		
		- elements_list : the element list in which the choice has to be made
		- value: the initial value. If None, we take the first element of the
			list (unless if with_None is True, in which case, we take the None
			element
		- with_None : if True, add a None element to the list.
		"""
		if value==None:
			self.set_active_element(self.elements_list[0])
		else:
			self.set_active_element(value)
		
	
	def has_element(self,k):
		return k in self.elements_list
	
	def set_active_element(self,value,fromString=False):
		"""
		- fromString : if true, will look if the key corresponds to the string 
		version of each elements (usefull if None, is an element of the choice
		in which case, the string 'None' will return the good value).
		"""
		if fromString:
			dd = {unicode(k):k for k in self.elements_list}
			if value not in dd.keys():
				raise ValueError('the value is not in the elements list')
			self.active_element = dd[value]
		else:
			if value not in self.elements_list:
				raise ValueError('the value is not in the elements list')
			self.active_element = value
	
	

	def __eq__(self,other):
		if isinstance(other,self.__class__):
			return self.active_element == other.active_element
		else:
			return self.active_element == other
	def __ne__(self,other):
		return not self.__eq__(other)
	
	def __str__(self):
		return unicode(self.active_element)
		
	def __hash__(self):
		return self.active_element.__hash__()
	
	def copy(self):
		return self.__class__(self.active_element)
		
