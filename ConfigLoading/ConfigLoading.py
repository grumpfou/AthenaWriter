"""
This file deals with the words to add to the spell checker and the 
autocorrelation.
"""

######################### FileManagement importation #########################
import sys,os
d,f = os.path.split(__file__)
sys.path.append(os.path.join(d,'../'))
# sys.path.append('/home/dessalles/Programmation/Python/AthenaWriterNew1/FileManagement/')
from FileManagement.FileManagement import FMFileManagement

##############################################################################
from ConfigLoadingConstants import CLConstants

def get_file_list(filepath,where='all',local_dir=None):
	"""
	where in ['global','user','local','all']
	"""
	res = []
	if where=='all' or where == 'global':
		d,f = os.path.split(__file__)
		p_g = os.path.abspath(os.path.join(d,'..',CLConstants['GLOBAL_DIR'],
																	filepath))
		res.append((p_g,os.path.exists(p_g)))
		
	if where=='all' or where == 'user':
		p_u = os.path.expanduser(os.path.join(CLConstants['USER_DIR'],
																	filepath))
		res.append((p_u,os.path.exists(p_u)))
		
	if where=='all' or where == 'local':
		if local_dir!=None:
			p_l = os.path.abspath(os.path.join(local_dir,
											CLConstants['LOCAL_DIR'],filepath))
			res.append((p_l,os.path.exists(p_l)))
		else:
			res.append((None,False))
	return res
	

class CLSpelling:
	filepath = './.spelling.txt'
	
	@staticmethod
	def get_values(where='all',local_dir=None):
		"""
		where in ['global','user','local','all']
		"""
		file_list = get_file_list(CLSpelling.filepath,where=where,
														local_dir=local_dir)
		
		list_words = []
		for p,exists in file_list:
			if exists:
				list_words += CLSpelling.open(p)
		return list_words
	
	@staticmethod
	def open(filepath):
		file=FMFileManagement.open(filepath,output='readlines')
		
		res=[]
		# We read the config file
		file=FMFileManagement.open(filepath,output='readlines')

		# We fill the res with the values contained into the file
		for ligne in file:
			ligne=ligne.strip()
			ligne = ligne.split(' ')
			res.append(ligne)
		return res
	
	@staticmethod	
	def save(words,filepath):
		words.sort()
		words = list(set(words))
		to_save = '\n'.join(words)
		
		file=FMFileManagement.save(to_save,filepath=filepath)
	
	@staticmethod
	def add_words(words,where,local_dir=None):
		"""
		where in ['global','user','local']
		"""
		assert where in ['global','user','local']
		assert where!='local' or local_dir!=None
		l = CLSpelling.get_values(where=where,local_dir=local_dir)
		words = list(words)
		l += words
		file_list = get_file_list(CLSpelling.filepath,where=where,
														local_dir=local_dir)
		for fp,exists in file_list:
			print 'fp : ',fp
			CLSpelling.save(words=l,filepath=fp)
		
		
class CLAutoCorrection:
	filepath = './.autocorrection.txt'
	
	@staticmethod
	def get_values(where='all',local_dir=None):
		"""
		where in ['global','user','local','all']
		"""
		file_list = get_file_list(CLAutoCorrection.filepath,where=where,
														local_dir=local_dir)
		
		dict_words = {}
		for p,exists in file_list:
			if exists:
				dict_words = dict(dict_words.items()+
											CLAutoCorrection.open(p).items())
		return dict_words
	
	@staticmethod
	def open(filepath):
		file=FMFileManagement.open(filepath,output='readlines')
		
		res={}
		# We read the config file
		file=FMFileManagement.open(filepath,output='readlines')

		# We fill the res with the values contained into the file
		for ligne in file:
			ligne=ligne.strip()
			i=ligne.find(' ')
			if i!= -1:
				k=ligne[:i]
				v=ligne[i:].strip()
				res[k]=v
		return res
		
	@staticmethod	
	def save(words,filepath):
		words_keys = words.kays()
		words_keys.sort()
		words = [(k,words[k]) for k in words_keys]
		words = [' '.join(w) for w in words]
		to_save = '\n'.join(words)
		file=FMFileManagement.open(to_save,filepath=filepath)		
	
	@staticmethod
	def add_words(words,where,local_dir=None):
		"""
		- where: where to save, shoulbe in ['global','user','local']
		- words : the dict to add; if it is a tuple then d[words[0]] = words[1]
		"""
		assert where in ['global','user','local']
		assert where!='local' or local_dir!=None
		d = CLAutoCorrection.get_values(where=where,local_dir=local_dir)
		words = dict(words)
		d = dict(d.items()+words.items())
		file_list = get_file_list(CLSpelling.filepath,where=where,
														local_dir=local_dir)
		for fp,exists in file_list:
			CLSpelling.save(words=d,filepath=fp)
			
			
if __name__=='__main__':
	print 'CLSpelling.get_values() : ',CLSpelling.get_values()
	CLSpelling.add_words(['test1'],where='global')