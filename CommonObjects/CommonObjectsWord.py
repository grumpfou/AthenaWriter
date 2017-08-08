"""
Part of the AthenaWriter project. Written by Renaud Dessalles
Contains classes relative to Words, the reason I need theses classes is that I needed to
deal with the capital letters.
"""
import string

class COWordTools:
	IND_LOWER		= 1
	IND_FIRST_CAP	= 2
	IND_ALL_CAP		= 4
	
	IND_ALL = IND_LOWER|IND_FIRST_CAP|IND_ALL_CAP
	
	@staticmethod
	def whatID(word):
		"""
		return 1 ( IND_LOWER ) if the first letter is not a capital
		return 2 ( IND_FIRST_CAP ) if the first letter is a capital (and not the rest)
		return 4 ( IND_ALL_CAP ) if the all the letters are capitals
		"""
		
		# if the word is single capital then it return IND_FIRST_CAP
		if len(word)==0:
			return False
		elif word.isupper():
			if len(word)==1:
				return COWordTools.IND_FIRST_CAP
			else:
				return COWordTools.IND_ALL_CAP
		elif word[0].isupper():
			return COWordTools.IND_FIRST_CAP
		else:
			return COWordTools.IND_LOWER

	@staticmethod
	def toID(word,id):
		# return a correspondant version of the word the corresponding ID
		# Deals with composed word, for instance:
		# COWordTools.toID("jean-louis",COWordTools.IND_FIRST_CAP) gives "Jean-Louis"
		word=str(word)
		if id==COWordTools.IND_FIRST_CAP:
			word=string.capwords(word,sep='-')

				
		elif id==COWordTools.IND_ALL_CAP:
			word=word.upper()
		return word



class COWordDico (dict):
	"""A dictionary reimplementation of the words that is case sensitive. It is 
	a dictionary that has in key the word in whatever case. The attribute will 
	be a tuple containing the corresponding word and it's ID (specified in 
	COWordTools)."""
	def __init__(self,d):
		dict.__init__(self)
		
		self.update(d)
		
	def update(self,d):
		if not isinstance(d,dict):
			d=dict(d)
		for k,v in list(d.items()):
			self[k] = v
	
	def __setitem__(self,k,v,id = None):
		k = str(k)
		v = str(v)
		self.addWord(k,v)
		
	def addWord(self,k,v,id=None):
		v=str(v).lower()
		if id==None:
			id = COWordTools.whatID(k)
			if id == COWordTools.IND_LOWER:
				id=COWordTools.IND_ALL
		
		k = str(k).lower()
		
		dict.__setitem__(self,k,(v,id))
	
	def get(self,word,d=None):
		try:
			return self[word]
		except KeyError:
			return d
			
	def __getitem__(self,word):
		word=str(word)
		word_tmp=word.lower()	
		res = dict.__getitem__(self,word_tmp)
	
		id=COWordTools.whatID(word)
		if id|res[1]>0:
			return COWordTools.toID(res[0],id)
		else: 
			raise KeyError(word)
	
	def input_from_dict(self,data_dict):
		for key,value in list(data_dict.items()):
			self[key]=value
			
	def has_key(self,k):
		k_tmp = k.lower()
		if dict.has_key(self,k_tmp):
			
			id = COWordTools.whatID(k)
			res = dict.__getitem__(self,k_tmp)
			if id&res[1]==0:
				return False
			return True
		return False
		




'''
# This static class allows to detect the format of a word and to change it:
class COWordTools:
	IND_LOWER		= 1
	IND_FIRST_CAP	= 2
	IND_ALL_CAP		= 4
	
	IND_ALL = IND_LOWER|IND_FIRST_CAP|IND_ALL_CAP
	
	@staticmethod
	def whatID(word):
		"""
		return 1 ( IND_LOWER ) if the first letter is not a capital
		return 2 ( IND_FIRST_CAP ) if the first letter is a capital (and not the rest)
		return 4 ( IND_ALL_CAP ) if the all the letters are capitals
		"""
		if the word is single cpaital then it return IND_FIRST_CAP
		
		if len(word)==0:
			return False
		elif word.isupper():
			if len(word)==1:
				return COWordTools.IND_FIRST_CAP
			else:
				return COWordTools.IND_ALL_CAP
		elif word[0].isupper():
			return COWordTools.IND_FIRST_CAP
		else:
			return COWordTools.IND_LOWER

	@staticmethod
	def toID(word,id):
		# return a correspondant version of the word the corresponding ID
		# Deals with composed word, for instance:
		# COWordTools.toID("jean-louis",COWordTools.IND_FIRST_CAP) gives "Jean-Louis"
		word=unicode(word)
		if id==COWordTools.IND_FIRST_CAP:
			word=string.capwords(word,sep=u'-')

				
		elif id==COWordTools.IND_ALL_CAP:
			word=word.upper()
		return word
	
    # whatID = staticmethod(whatID)
    # toID = staticmethod(toID)

class COWordSet (set):
	"""This class is mainly a dictionary that deals with capitalization
	every word is goes with an id that stipulate the different version of 
	capitilization possible for the word.
	the main attribute : WordSet.dico has as key the word in the lower version 
	and the value is the corresponding IDs. For instance
	WordSet.addWord("apple",COWordTools.IND_LOWER|COWordTools.IND_FIRST_CAP) 
	will add the word "apple" which can be written with a first letter as a 
	capital or not, but not with all letters as capitals."""
	
	
	def __init__(self,iterable):
		self.dict_id={}
		for v in iterable:
			self.add(v)
			
	def add(self,word,id=None):
		if id==None:
			id = COWordTools.whatID(word)
			if id == COWordTools.IND_LOWER:
				id=COWordTools.IND_ALL
		word=unicode(word).lower()
		self.dict_id[word]=id
		set.add(self,word)
	
	def remove(self,word):
		id = COWordTools.whatID(word)
		word = unicode(word).lower()
		if not self.dict_id.has_key(word):
			raise KeyError(word)
		if (id&self.dict_id[word])==0:
			raise KeyError(word)
		set.remove(self,word)
		self.dict_id.pop(word)
		
	# def __init__(self,data_list=None):
		# self.dico={}
		# if data_list!=None:
			# self.input_from_list(data_list)
	
	def add(self,word_entry,id=None): # if id is None, all the version will be possible
		if id==None:
			id = COWordTools.whatID(word_entry)
			if id == COWordTools.IND_LOWER:
				id=COWordTools.IND_ALL
		word_entry=unicode(word_entry).lower()
		
		
		self.dict_id[word_entry]=id
	
	def __contains__(self,word):# tell if the word is in the strucure with the same capitilization.
		word=unicode(word)
		word_tmp = unicode(word).lower()
		coresp=self.dict_id.get(word_tmp,False)
		if not coresp: return False
		id = COWordTools.whatID(word)
		if (id&coresp)>0:
			return True
		return False
	# def pop(self):
		# word=unicode(word).lower()
		# set.pop(self,word)
		
	# def removeWord(self,word): # remove the word (whatever it version)
		# word=unicode(word).lower()
		# if self.dico.has_key(word):
			# self.dico.remove(word)
			# return True
		# else:
			# return False
	
	# def yieldSet(self):
		# list_id=[COWordTools.IND_LOWER,COWordTools.IND_FIRST_CAP,COWordTools.IND_ALL_CAP]
		# for word,id in self.dico.items():
			# for id_tmp in list_id:
				# if id_tmp&id>0:
					# yield COWordTools.toID(word,id_tmp)

		
	# def input_from_list(self,data_list): # add the words contained in the list their own capitalization
		# for data in data_list:
			# id=COWordTools.whatID(data)
			# self.addWord(data,id)
	
	# def get(self,word):
		# word=unicode(word)
		# word_tmp=unicode(word).lower()
		# coresp=self.dico.get(word_tmp,False)
		# if not coresp: return False
		# id=COWordTools.whatID(word)
		# if id|coresp[1]>0:
			
			# return COWordTools.toID(coresp[0],id)
		# else: return False
# 	
		
	
class COWordDico (dict):
	def __init__(self,*args,**kargs):
		dict.__init__(self,*args,**kargs)
	
	def __getitem__(se
	
	
class COWordDico (dict):
	"""A dictionary reimplementation of the words that is case sensitive. It is 
	a dictionary that has in key the word in whatever case. The attribute will 
	be a tuple containing the corresponding word and it's ID (specified in 
	COWordTools)."""
	def __init__(self,data_dict=None):
		dict.__init__(self)
		if data_dict!=None:
			self.input_from_dict(data_dict)
	
	
	def __setitem__(self,k,v):
		print 'coucou1',k,v
		k = unicode(k)
		v = unicode(v)
		self.addWord(k,v)
		
	def addWord(self,k,v,id=None):
		v=unicode(v).lower()
		if id==None:
			id = COWordTools.whatID(k)
			if id == COWordTools.IND_LOWER:
				id=COWordTools.IND_ALL
			print 'id : ',id,k
		
		k = unicode(k).lower()
		
		dict.__setitem__(self,k,(v,id))
	
	def get(self,word,d):
		try:
			return self[word]
		except KeyError:
			return d
			
	def __getitem__(self,word):
		word=unicode(word)
		word_tmp=word.lower()	
		res = dict.__getitem__(self,word_tmp)
	
		id=COWordTools.whatID(word)
		if id|res[1]>0:
			return COWordTools.toID(res[0],id)
		else: 
			raise KeyError(word)
	
	def input_from_dict(self,data_dict):
		for key,value in data_dict.items():
			self[key]=value
			
	def has_key(self,k):
		k_tmp = k.lower()
		if dict.has_key(self,k_tmp):
			
			id = COWordTools.whatID(k)
			res = dict.__getitem__(self,k_tmp)
			if id&res[1]==0:
				return False
			return True
		return False
	'''	
if __name__=='__main__':
	d = COWordDico({'Toto':'totoro','titi':'Titiri'})
	
	print('Tests Dict')
	print("1",d["Toto"]=='Totoro')
	# print 'd["Toto"] : ',d["Toto"]
	print("2",("toto" in d)==False)
	print("3",("Toto" in d)==True)
	print("4",("titi" in d)==True)
	print("5",("Titi" in d)==True)
	print("6",d["Titi"]=='Titiri')
	print("7",d["titi"]=='titiri')
	print("8",d["TITI"]=='TITIRI')
	
	
	# s = COWordSet(['toto','tata','Titi'])
	# print "1",'toto' in s
	# print "2",'Toto' in s
	# print "4",('titi' in s)==False
	# print "5",'Titi' in s
	
