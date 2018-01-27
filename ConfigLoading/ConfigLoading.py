"""
This file deals with the words to add to the spell checker and the
autocorrelation and the preferences.
"""

######################### FileManagement importation #########################
import sys,os
d,f = os.path.split(__file__)
sys.path.append(os.path.join(d,'../'))
# sys.path.append('/home/dessalles/Programmation/Python/AthenaWriterNew1/FileManagement/')
from FileManagement.FileManagement import FMTextFileManagement,FMZipFileManagement
##############################################################################

from .ConfigLoadingPreferences import CLPreferences
import pathlib



class CLAbstract:
	""" Abstract class that will be inherited by classes that deals with
	specific aspects of the configuration.

	Configuration can be things like preferences, spelling words,
	auto-correction, etc. The configuration can be defined at the global level
	(in the athw source code level), at the user level (under the '.athena'
	directory in the user home), locally (in the same directory of the file),
	or specific to the file considered.
	"""
	filepath = None # to reimplement, represent the name of the file in which
		# are saved the configuration

	whereFiles = ['global','user','local','file']
	# Where wan be searched the different configurations:
	# - global : in the source code of the athw
	# - user : under the '.athena' directory in the user home
	# - local : in the same directory as in local_file
	# - file : in the local_file

	class Error (Exception):
		def __init__(self,raison,where=None):
			"""Special Error function for the config file """
			self.raison	= raison
			self.where = where

		def __str__(self):
			res = "In the config %s in `%s`:\n"%(self.filename,str(self.where))+self.raison
			return res.encode('ascii','replace')


	def __init__(self,local_file=None):
		self.local_file = local_file
		self.dictConfig= { where:None for where in self.whereFiles}
		self.getConfig(where='all')

	def get_file_list(self,filepath=None,where='all'):
		"""
		Will get all the files located in the different position:
		- filepath: the name of the file to search (bu default, it is
			self.filepath)
		- where: should be in `whereFiles` or be 'all' (in which case, it
			return the list of all the config files)

		Returns :
		- res: a list of tuples (where,path,exists) with `where` corresponds to
			['file','local','user','global'], `path` config file path associated
			to `where`  and `exists` True if the file exists
		"""
		assert where in self.whereFiles or where=='all'
		if filepath==None: filepath=self.filepath

		if where=='all': where = self.whereFiles
		else: where=[where]

		res = []
		if 'global' in where:
			d,f = os.path.split(__file__)
			p_g = pathlib.Path(d)/'..'/CLPreferences['GLOBAL_DIR']/filepath
			# os.path.abspath(os.path.join(d,'..',
			# 							str(CLPreferences['GLOBAL_DIR']), filepath))
			res.append(('global',str(p_g),p_g.exists()))

		if 'user' in where:
			p_u = CLPreferences['USER_DIR']/filepath
			p_u = p_u.expanduser()
			# os.path.expanduser(os.path.join(str(CLPreferences['USER_DIR']),
			# 															filepath))
			res.append(('user',str(p_u),p_u.exists()))

		if 'local' in where:
			if self.local_file!=None:
				p_l = pathlib.Path(self.local_file).parent/CLPreferences['LOCAL_DIR']/filepath
				# os.path.abspath(os.path.join(local_dir,
				# 								CLPreferences['LOCAL_DIR'],filepath))
				res.append(('local',str(p_l),p_l.exists()))
			else:
				res.append(('local',None,False))

		if 'file' in where:
			if self.local_file!=None:
				p_l = pathlib.Path(self.local_file)/filepath
				# os.path.abspath(os.path.join(local_dir,
				# 								CLPreferences['LOCAL_DIR'],filepath))
				zipfile = FMZipFileManagement.splitZipfilepath(p_l)
				if zipfile: zipfile = zipfile[2] # if the zipfile exists, look if the filename exists inside the zipfile
				res.append(('file',str(p_l),zipfile))
			else:
				res.append(('file',None,False))

		return res

	def getConfig(self,where='all',errors='print'):
		"""Will return the lines of config file:
		- where: should be in `whereFiles`, if is 'all', then it concatenates
			all the files of `whereFiles`
		- errors: in ['raise','print','skip']
			In the case of line line of the file not well written, it either:
			- it raises the error if it is 'raise'
			- it prints the error if it is 'print'
			- it skips the error if it is 'skip'
		"""
		assert errors in ['raise','print','skip']
		file_list = self.get_file_list(self.filepath,where=where)

		for w,filepath,exists in file_list:
			self.dictConfig[w]=None
			if exists:
				if w == 'file':
					zipfile = FMZipFileManagement.splitZipfilepath(filepath)
					lines = FMZipFileManagement.open(
								zipfilepath=zipfile[0],
								filename=zipfile[1],
								output='readlines',
								)
				else:
					 lines = FMTextFileManagement.open(filepath,
															output='readlines')
				for l in lines:
					try :
						# We call the method interpretLigne to seperate the key from the values
						self.interpretLigne(l,w)
					except self.Error as e:
						if errors=='raise':
							raise e
						elif  errors=='print':
							print(e)
						elif errors=='skip':
							pass

	def saveConfig(self,where='all',**kargs):
		"""Save the information contained in self.dictConfig in the
		corresponding  config file.
		- where: specify the file where to save the information. Should be
			either in self.whereFiles or being 'all'.
		- **kargs: possible additional arguments to send to self.getText method
		"""
		file_list = self.get_file_list(self.filepath,where=where)

		for w,filepath,exists in file_list:
			text = self.getText(where=where,**kargs)
			if len(text)>0 or exists: # To be sure to erase if necessary
				if w=='file':
					zipfile = FMZipFileManagement.splitZipfilepath(filepath)
					FMZipFileManagement.save(text,
							zipfilepath=zipfile[0],
							filename=zipfile[1],
							)
				else:
					FMTextFileManagement.save(text=text,filepath=filepath)

	def changeFile(self,local_file):
		self.local_file = local_file
		self.getConfig('file')
		self.getConfig('local')

	def getText(self,where):
		"""Transform the information of self.dictConfig[where] in a string to
		that can be output in a file.
		"""
		raise NotImplementedError
		# To reimplement

	def interpretLigne(self,line,where):
		"""Interpret the line and update the self.dictConfig[where] accordingly"""
		raise NotImplementedError
		# To reimplement

	def update(self,new_information,where):
		raise NotImplementedError
		# To reimplement


	def getValues(self):
		"""Returns all the informations"""
		raise NotImplementedError
		# To reimplement


class CLSpelling (CLAbstract):
	filepath = './.spelling.txt'

	def interpretLigne(self,line,where):
		line=line.strip()
		line = set(line.split(' '))
		if self.dictConfig[where] == None:
			self.dictConfig[where] = line
		else:
			self.dictConfig[where].update(line)

	def getText(self,where):
		assert where in self.whereFiles
		if self.dictConfig[where] is None:
			return ""
		else:
			return '\n'.join(self.dictConfig[where])


	def update(self,words,where):
		"""
		where in ['global','user','local','file']
		"""
		assert where in self.whereFiles
		if self.dictConfig[where] is None:
			self.dictConfig[where] = set(words)
		else:
			self.dictConfig[where].update(set(words))

		if self.local_file != None or where not in {'local','file'}: # if it can be saved
			self.saveConfig(where)

	def getValues(self):
		d = set()
		for k in self.whereFiles:
			if self.dictConfig[k]!=None:
				d.update(set(self.dictConfig[k]))
		return d

# def new config loading
class CLAutoCorrection (CLAbstract):
	filepath = './.autocorrection.txt'


	def interpretLigne(self,line,where):
		assert where in self.whereFiles
		line=line.strip()
		i=line.find(' ')
		if i!= -1:
			k=line[:i]
			v=line[i:].strip()

			if self.dictConfig[where] == None:
				self.dictConfig[where] = {k:v}
			else:
				self.dictConfig[where][k] = v

	def getText(self,where):
		assert where in self.whereFiles+['all']

		words = self.dictConfig[where]
		if words is None:
			return ""

		words_keys = list(words.keys())
		words_keys.sort()
		words = [(k,words[k]) for k in words_keys]
		words = [' '.join(w) for w in words]
		to_save = '\n'.join(words)

		return to_save

	def update(self,words,where):
		"""
		- words : the dict to add; if it is a tuple then d[words[0]] = words[1]
		- where: where to save, shoulbe in ['global','user','local','file']
		"""
		assert where in self.whereFiles
		self.dictConfig[where].update(dict(words))
		self.saveConfig(where)

	def getValues(self):
		d = dict()
		for k in self.whereFiles:
			if self.dictConfig[k]!=None:
				d.update(self.dictConfig[k])
		return d


class CLPreferencesFiles (CLAbstract):

	filepath = './config_AthenaWriter.txt'
	whereFiles = ['global','user'] # We do not allow the local nor the file config

	comment_sign='#' #The sign that will indicate that what is remaining from the line
						# is a comment
	exception_sign='\\' # '\#' '\|' will not considered a special sign in the file
	entry_separator_sign=':' # a constant in the file shall have the form of
								# " constant_key : constant_value "
	separator_sign='|' #the values shall be separated by this sign



	def interpretLigne(self,ligne,where):
		"""
		Will interpret the line : it will separate the entry from the value
		(separated by entry_separator_sign and the values from each others by
		self.separator_sign.
		It will return :
		- (entry,value) : if there is only one value
		- (entry,[value1,value2,...]) : if there is more that one value
		"""
		assert where in self.whereFiles
		## CLEANING:
		ligne=ligne.strip() #we remove the spaces at the beginning
				# end at the end.
		if ligne == "":
			return False #if it is empty, we consider nothing
		elif ligne[0]==self.comment_sign:
			return False #if it all the line is a comment, we consider nothing

		i = ligne.find(self.comment_sign)
		while i>0:
			if ligne[i-1]!=self.exception_sign:
				ligne = line[:i]
				break
			i = ligne.find(self.comment_sign,i+1)

		## INTERPRET_LIGNE
		dp_pos=ligne.find(self.entry_separator_sign) #the position of the separator
		if dp_pos<0:
			raise self.Error( "This line has no entry-value separator:%s"%line )

		# We find the entry
		entry 	 = ligne[:dp_pos]
		entry	 = entry.strip() # get rid of the spaces from each part

		if dp_pos==len(ligne)-1: # If there is no value
			return entry, ""

		# We find the values
		line_tmp = ligne[dp_pos+1:]
		line_tmp = line_tmp.split(self.separator_sign)
		line_tmp = [value.strip() for value in line_tmp]


		# We return the result depending on the number of values
		if len(line_tmp)==1:
			v = line_tmp[0]
		else:
			v = line_tmp

		if self.dictConfig[where] is None:
			self.dictConfig[where] = {entry:v}
		else:
			self.dictConfig[where] [entry] = v


	def getText(self,where,descriptions=None):
		"""
		Return a text that corresponds to the information contained in
		self.dictConfig[where]
		- where: should be in self.whereFiles
		- descriptions: dict that contains the description corresponding keys
			of dict_to_save
		"""
		assert where in self.whereFiles+['all']
		if descriptions==None: descriptions={}
		dict_to_save = self.dictConfig[where]

		s = self.comment_sign+ " Preference for the software AthenaWriter."

		for k,v in list(dict_to_save.items()):
			if k in descriptions:
				s += CLPreferencesFiles.comment_sign+' '+ descriptions[k]+'\n'

			if type(v) == list:
				l = [str(a) for a in v]
				s += k+' '+CLPreferencesFiles.entry_separator_sign+' '
				s+= CLPreferencesFiles.separator_sign.join(l) +'\n'

			elif type(v) == dict:
				l = [str(kk)+' '+str(vv) for kk,vv in list(v.items())]
				s += k+' '+CLPreferencesFiles.entry_separator_sign+' '
				s+= CLPreferencesFiles.separator_sign.join(l) +'\n'

			else:
				s += k+' '+CLPreferencesFiles.entry_separator_sign+' '
				s += str(v)+'\n'


		return s

	def getValues(self):
		d = dict()
		for k in self.whereFiles:
			if self.dictConfig[k]!=None:
				d.update(self.dictConfig[k])
		return d

	def update(self,other_dict, where):
		"""
		- other_dict: the dictionary containing the information that need to be
			included in self.dictConfig[where]
		- where: should be in self.whereFiles
		"""
		assert where in self.whereFiles
		self.dictConfig[where].update(other_dict)



class CLLastFiles(CLAbstract):
	filepath = './last_files.txt'
	whereFiles = ['user']


	# def addFile(self,file):
	# 	file=os.path.abspath(file)
	# 	if file in self.list_files:
	# 		self.list_files.remove(file)
	# 	self.list_files.insert(0,file)
	# 	if CLPreferences['LAST_FILE_SKIP_NON_EXISTING']:
	# 		self.check_existing()
	# 	if len(self.list_files)>= CLPreferences['LAST_FILE_LENGTH']:
	# 		self.list_files=self.list_files[:CLPreferences['LAST_FILE_LENGTH']]




	def getText(self,where):
		"""
		Return a text that corresponds to the information contained in
		self.dictConfig[where]
		- where: should be in self.whereFiles
		"""
		assert where in self.whereFiles+['all']
		list_files = self.dictConfig[where]
		if list_files==None: return ''

		list_files = [l for l in list_files]
		return '\n'.join(list_files)

	def interpretLigne(self,line,where):
		assert where in self.whereFiles
		line=line.strip()
		if self.dictConfig[where] == None:
				self.dictConfig[where] = [line]
		else:
			self.dictConfig[where].append(line)

	def getValues(self):
		res = []
		for k in self.whereFiles:
			if self.dictConfig[k]!=None:
				list_files = self.dictConfig[k]

				for i,f in enumerate(list_files):
					if  (not CLPreferences['LAST_FILE_SKIP_NON_EXISTING']) or \
															os.path.exists(f):
						res.append(f)
		return res

	def update(self,newfiles,where='user'):
		assert where in self.whereFiles
		for f in newfiles:
			f=os.path.abspath(f)

			while f in  self.dictConfig[where]:
				self.dictConfig[where].remove(f)
			self.dictConfig[where].insert(0,f)
		if len(self.dictConfig[where])>= CLPreferences['LAST_FILE_LENGTH']:
			self.dictConfig[where]=self.dictConfig[where][:CLPreferences['LAST_FILE_LENGTH']]
