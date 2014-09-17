import string


from FileManagement import FMFileManagement
from FileManagementConstants import *

class FMConfigFileError (BaseException):
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

class FMFileConstants (FMFileManagement):
	
	comment_sign='#' #The sign that will indicate that what is remaining from the line 
						# is a comment
	exception_sign='\\' # '\#' '\|' will not considered a special sign in the file
	entry_separator_sign=':' # a constant in the file shall have the form of
								# " constant_key : constant_value "
	separator_sign='|' #the values shall be separated by this sign
	
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
		file,equivalent_line = FMFileConstants.clean_file(file)
		
		# We fill the result_dictionary with the values contained into the file
		for i,ligne in enumerate(file):
			try :
				# We call the method interpret_ligne to seperate the key from the values
				e,v=FMFileConstants.interpret_ligne(ligne)
				result_dictionary[str(e)]=v
			except FMConfigFileError , e:
				print 'ligne : ',ligne.encode('utf-8')
				e_other = FMConfigFileError(e.raison,
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
			elif ligne[0]==FMFileConstants.comment_sign:
				pass #if it all the line is a comment, we consider nothing
			else:
				for i in range(1,len(ligne)):
					# if we encounter the comment_sign, we get rid of the end 
					# of the line
					if ligne[i]==FMFileConstants.comment_sign and ligne[i-1]!=FMFileConstants.exception_sign:
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
		dp_pos=ligne.find(FMFileConstants.entry_separator_sign) #the position of the separator
		if dp_pos<0:
			raise FMConfigFileError( " This line has no entry-value separator. " )
		
		# We find the entry
		entry 	 = ligne[:dp_pos]
		entry	 = entry.strip() # get rid of the spaces from each part
		
		if dp_pos==len(ligne)-1: # If there is no value
			return entry, ""
		
		# We find the values
		line_tmp = ligne[dp_pos+1:]
		line_tmp = line_tmp.split(FMFileConstants.separator_sign)
		line_tmp = [value.strip() for value in line_tmp]
		
		# We return the result depending on the number of values
		if len(line_tmp)==1:
			return entry, line_tmp[0]
		else:
			return entry, line_tmp
			
	
