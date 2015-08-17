class DVError (StandardError):pass
class DVContrainedDict(dict):
	def __init__(self,a):
		"""
		If a is a list of string: it will be the keys and all the values will 
		be initiated to None
		"""
		dict.__init__(self)
		if type(a)==list:
			# self.init_keys(a)
			for k in a:
				self.__setitem__(k,None,False)
		elif type(a)==dict:
			for k,v in a.items():
				self.__setitem__(k,v,False)
		else:
			raise ValueError('ContrainedDict should have in entry only a '+\
				'dict or a list.')
	
	def __setitem__(self,k,v,protected=True):
		if protected and k not in self.keys():
			raise KeyError('The key '+k+' is unkown for this ContrainedDict.')
		return dict.__setitem__(self,k,v)
	def __getitem__(self,k,protected=True):
		if protected and k not in self.keys():
			raise KeyError('The key '+k+' is unkown for this ContrainedDict.')
		return dict.__getitem__(self,k)

class DVChoice:
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
		