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
import string

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
		file=FMFileManagement.save(to_save,filepath=filepath)		
	
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
 
			

class CLPreferences:
	class Error (StandardError):
		def __init__(self,raison,line=False,file=False):
			"""Special Error function for the config file (is normaly able to gives 
			the line of the error in the config file, but it is approximative ^^"""
			self.raison	= raison
			self.line	= line
			self.file	= file
			print self
		def __str__(self):
			res=""
			if self.file :
				res+="In file "+self.file+" : "
			if self.line:
				res+="To line "+str(self.line)+" : "
			
			res+=self.raison
			
			return res.encode('ascii','replace')
	
	
	
	filepath = './config_AthenaWriter.txt'
	
	comment_sign='#' #The sign that will indicate that what is remaining from the line 
						# is a comment
	exception_sign='\\' # '\#' '\|' will not considered a special sign in the file
	entry_separator_sign=':' # a constant in the file shall have the form of
								# " constant_key : constant_value "
	separator_sign='|' #the values shall be separated by this sign
	
	@staticmethod
	def get_values(where='all'):
		"""Class that will deal with the preference files.
		where in ['all','global','user']
		"""
		file_list = get_file_list(CLPreferences.filepath,where=where,
														local_dir=None)
		
		dd = {}
		for p,exists in file_list:
			if exists:
				dd.update(CLPreferences.open(p))
		return dd
		
	###########################################################################
	@staticmethod
	def open(pathway=None):
		"""
		- pathway : the path to the "config.txt" file
		"""
		
		pathway=pathway
		result_dictionary={}
		
		# We read the config.txt file
		file=FMFileManagement.open(pathway,output='readlines')

		# We get rid of the comments and empty lines
		file,equivalent_line = CLPreferences.clean_file(file)
		
		# We fill the result_dictionary with the values contained into the file
		for i,ligne in enumerate(file):
			try :
				# We call the method interpret_ligne to seperate the key from the values
				e,v=CLPreferences.interpret_ligne(ligne)
				result_dictionary[str(e)]=v
			except CLPreferences.Error , e:
				print 'ligne : ',ligne.encode('utf-8')
				e_other = CLPreferences.Error(e.raison,
							line=equivalent_line[i],
							file=pathway)
				
				raise	e_other
				
		return result_dictionary
		
	@staticmethod	
	def clean_file(file):
		"""
		This function will get rid of the empty line and the comments in file.
		"""
		new_file=[]
		equivalent_line=[]
		i=0
		
		for indice, ligne in enumerate(file):
			ligne=string.strip(ligne) #we remove the spaces at the beginning 
					# end at the end.
			if ligne == "":
				pass #if it is empty, we consider nothing
			elif ligne[0]==CLPreferences.comment_sign:
				pass #if it all the line is a comment, we consider nothing
			else:
				for i in range(1,len(ligne)):
					# if we encounter the comment_sign, we get rid of the end 
					# of the line
					if ligne[i]==CLPreferences.comment_sign and ligne[i-1]!=CLPreferences.exception_sign:
							new_file.append(ligne[:i])
							break
				else:
					new_file.append(ligne)
				
				equivalent_line.append(i)
			i+=1
		return new_file,equivalent_line
	
	@staticmethod
	def interpret_ligne(ligne):
		"""
		Will interpret the line : it will separate the entry from the value 
		(separated by entry_separator_sign and the values from each others by  
		self.separator_sign.
		It will return :
		- (entry,value) : if there is only one value
		- (entry,[value1,value2,...]) : if there is more that one value
		"""
		dp_pos=ligne.find(CLPreferences.entry_separator_sign) #the position of the separator
		if dp_pos<0:
			raise CLPreferences.Error( " This line has no entry-value separator. " )
		
		# We find the entry
		entry 	 = ligne[:dp_pos]
		entry	 = entry.strip() # get rid of the spaces from each part
		
		if dp_pos==len(ligne)-1: # If there is no value
			return entry, ""
		
		# We find the values
		line_tmp = ligne[dp_pos+1:]
		line_tmp = line_tmp.split(CLPreferences.separator_sign)
		line_tmp = [value.strip() for value in line_tmp]
		
		# We return the result depending on the number of values
		if len(line_tmp)==1:
			return entry, line_tmp[0]
		else:
			return entry, line_tmp
	

	@staticmethod	
	def save(to_save,filepath):
		file=FMFileManagement.save(to_save,filepath=filepath)
	
	@staticmethod
	def replace(to_save,where='user'):
		"""
		where in ['user','local']
		"""
		assert where in ['global','user']
		
		file_list = get_file_list(CLPreferences.filepath,where=where,
														local_dir=None)
		for fp,exists in file_list:
			CLPreferences.save(to_save,filepath=fp)
	
if __name__=='__main__':
	print 'CLSpelling.get_values() : ',CLSpelling.get_values()
	CLSpelling.add_words(['test1'],where='global')