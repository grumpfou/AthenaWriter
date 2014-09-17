from PyQt4 import QtGui, QtCore
import codecs
import os.path

class FMFileManagement:
	
	@staticmethod
	def save(text,filepath,encoding='utf-8',mode='w'):
		""" Function that will save the information contained in text into
		the file at filepath.
		- text: the unicode string to save into the path
		- filepath: the path of the file
		"""
		filepath = os.path.expanduser(filepath)
		fid = codecs.open(filepath, encoding=encoding, mode=mode)
		try :
			fid.write(text)
		finally:
			fid.close()
			
		return True
	
		
	@staticmethod
	def save_gui(text,dft_opening_saving_site=None,parent=None,extension=None,*args,**kargs):
		""" Function that will open a dialog window to save the file.
		- text : the unicode sstring to save into the file
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		- extension: the extension to consider
		"""
		if dft_opening_saving_site==None: dft_opening_saving_site='.'
		dialog= QtGui.QFileDialog(parent)
		if extension!=None:
			filepath = dialog.getSaveFileName(parent,"Select the file to save",dft_opening_saving_site,
					filter='*.'+extension)
		else :
			filepath = dialog.getSaveFileName(parent,"Select the file to save",dft_opening_saving_site)
		if filepath:
			filepath=unicode(filepath)
			FMFileManagement.save(text,filepath,*args,**kargs)
			return filepath
		return False
		
	@staticmethod
	def save_gui_filepath(dft_opening_saving_site=None,parent=None,extension=None,*args,**kargs):
		""" Function that will open a dialog window to get a filepath.
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		- extension: the extension to consider
		"""
		if dft_opening_saving_site==None: dft_opening_saving_site='.'
		dialog= QtGui.QFileDialog(parent)
		if extension!=None:
			filepath = dialog.getSaveFileName(parent,"Select the file to save",dft_opening_saving_site,
					filter='*.'+extension)
		else :
			filepath = dialog.getSaveFileName(parent,"Select the file to save",dft_opening_saving_site)
		if filepath:
			return filepath
		return False
	
	@staticmethod
	def open(filepath,with_codecs=True,output='read',mode='r',encoding='utf-8'):
		"""
		- filepath : the path of the file to open
		- with_codecs : if true, will give a utf-8 string
		- output : if output=='read' --> .read()
		           if output=='readlines' (or other) --> .readlines()
		- mode : the mode option in codecs.open function			
		- encoding: the encoding option in codecs.open function 
					(only if with_codecs is True)
		"""
		filepath = os.path.expanduser(filepath)		
		if with_codecs:
			fid = codecs.open(filepath, encoding=encoding, mode=mode)
		else :
			fid = open(filepath, mode=mode)
		try :
			if output=='read':
				res = fid.read()
			else:
				res = fid.readlines()
				
		finally:
			fid.close()
		return res
		
	@staticmethod
	def open_gui(dft_opening_saving_site=None,parent=None,*args,**kargs):
		""" Function that will open a dialog window to open a file.
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		Return	(filepath, text ):
		- filepath : the path to the file that is opened
		- text : the unicode string contained in the file		
		"""		
		if dft_opening_saving_site==None: dft_opening_saving_site='.'
		dialog= QtGui.QFileDialog(parent)
		filepath = dialog.	getOpenFileName(parent,"Select the file to open",dft_opening_saving_site)
		if filepath:
			filepath=unicode(filepath)
			res = FMFileManagement.open(filepath,*args,**kargs)
			return filepath,res
		return False
		
	@staticmethod
	def open_gui_filepath(dft_opening_saving_site=None,parent=None,*args,**kargs):
		""" Function that will open a dialog window to get a filepath to open.
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		Return	filepath:
		- filepath : the path to the file that is opened
		"""		
		if dft_opening_saving_site==None: dft_opening_saving_site='.'
		dialog= QtGui.QFileDialog(parent)
		filepath = dialog.	getOpenFileName(parent,"Select the file to open",dft_opening_saving_site)
		if filepath:
			filepath=unicode(filepath)
			return filepath
		return False
		

