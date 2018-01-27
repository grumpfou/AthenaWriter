from PyQt5 import QtGui, QtCore, QtWidgets
import codecs
import os.path
import math
import pathlib
import io
import zipfile

class FMTextFileManagement:

	@classmethod
	def save(cls,text,filepath,encoding='utf-8',mode='w',ext=None):
		""" Function that will save the information contained in text into
		the file at filepath.
		- text: the unicode string to save into the path
		- filepath: the path of the file
		- ext: if not None, with ensure the extension (put the dot in front of
			the extension)
		"""
		if type(filepath) == pathlib.Path:
			filepath = str(filepath)
		filepath = os.path.expanduser(filepath)
		if ext != None and  os.path.splitext(filepath)[1]!=ext:
			filepath = os.path.splitext(filepath)[0]+ext
		fid = codecs.open(filepath, encoding=encoding, mode=mode)
		try :
			fid.write(text)
		finally:
			fid.close()

		return True

	@classmethod
	def save_gui(cls,text,dft_opening_saving_site=None,parent=None,
		ext=False,filter="",*args,**kargs):
		""" Function that will open a dialog window to save the file.
		- text : the unicode sstring to save into the file
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		- ext: if not False, will force this extension
		"""
		filepath = cls.save_gui_filepath (
				dft_opening_saving_site=dft_opening_saving_site,
				parent=parent, ext=ext, filter=filter)

		if filepath:
			filepath=str(filepath)
			cls.save(text,filepath,*args,**kargs)
			return filepath
		return False

	@classmethod
	def save_gui_filepath(cls,dft_opening_saving_site=None,parent=None,ext=False,
													filter=""):
		""" Function that will open a dialog window to get a filepath.
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		- ext: if not False, will force this extension
		"""
		if dft_opening_saving_site==None: dft_opening_saving_site='.'
		elif type(dft_opening_saving_site)==pathlib.Path:
			dft_opening_saving_site = str(dft_opening_saving_site)

		dialog= QtWidgets.QFileDialog(parent)
		if ext:
			ext = ext.strip('.')
			while True: # This loop is to deal in the case where the filename
					# ending with the extension is already existing. For some
					# reason setDefaultSuffix does not work
				filepath = dialog.getSaveFileName(parent,
						"Select the file to save",
						dft_opening_saving_site,filter=filter)[0]
				if not filepath or filepath.endswith(ext):
					break
				filepath = os.path.splitext(filepath)[0]+'.'+ext
				if not os.path.exists(filepath):
					break
				dft_opening_saving_site,filename = os.path.split(filepath)
				r = QtWidgets.QMessageBox.warning(parent,
					"Select the file to save",
					"%s already exists. Do you want to replace it?"%filename,
					QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)

				if r== QtWidgets.QMessageBox.Yes:
					break
		else:
			filepath = dialog.getSaveFileName(parent,"Select the file to save",
									dft_opening_saving_site,filter=filter)[0]
		return filepath

	@classmethod
	def open(cls,filepath,with_codecs=True,output='read',mode='rU',encoding='utf-8'):
		"""
		- filepath : the path of the file to open
		- with_codecs : if true, will give a utf-8 string
		- output : if output=='read' --> .read()
		           if output=='readlines' --> .readlines()
		- mode : the mode option in codecs.open function
		- encoding: the encoding option in codecs.open function
					(only if with_codecs is True)
		"""
		if type(filepath) == pathlib.Path:
			filepath = str(filepath)
		filepath = os.path.expanduser(filepath)
		if with_codecs:
			fid = codecs.open(filepath, encoding=encoding, mode=mode)
		else :
			fid = open(filepath, mode=mode)
		try :
			if output=='read':
				res = fid.read()
			elif output=='readlines':
				res = fid.readlines()
			else:
				raise ValueError(
					"`output` parameter should be in {'read' or 'readlines'}"
					)
		finally:
			fid.close()
		return res

	@classmethod
	def open_gui(cls,dft_opening_saving_site=None,parent=None,filter="",*args,**kargs):
		""" Function that will open a dialog window to open a file.
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		Return	(filepath, text ):
		- filepath : the path to the file that is opened
		- text : the unicode string contained in the file
		"""
		filepath = cls.open_gui_filepath(
			dft_opening_saving_site=dft_opening_saving_site, parent=parent,
			filter=filter)

		if filepath:
			filepath=str(filepath)
			res = cls.open(filepath,*args,**kargs)
			return filepath,res
		return False

	@classmethod
	def open_gui_filepath(cls,dft_opening_saving_site=None,parent=None,filter="",*args,**kargs):
		""" Function that will open a dialog window to get a filepath to open.
		- dft_opening_saving_site : the path where to put the window at first
			(default : current path)
		- parent: the parent widget (for the dialog window to be modal)
		Return	filepath:
		- filepath : the path to the file that is opened
		"""
		if dft_opening_saving_site==None: dft_opening_saving_site='.'
		elif type(dft_opening_saving_site)==pathlib.Path:
			dft_opening_saving_site = str(dft_opening_saving_site)
		dialog= QtWidgets.QFileDialog(parent)
		filepath = dialog.getOpenFileName(parent,"Select the file to open",
								dft_opening_saving_site,filter=filter)[0]

		return filepath

	@classmethod
	def exists(cls,filepath):
		"""Look if the file exists, and if do propose to rename it.
		Return the new filepath (False is canceled)"""
		if type(filepath) == pathlib.Path:
			filepath = str(filepath)

		if not os.path.exists(filepath):
			return filepath

		filepath_start = filepath[:]
		max_ite = 1000 # NOT A CONSTANT FOR DIFFICULTIES TO DEFINE A CONSTANT
													# BEFORE IMPORTING THEM
		i = 0
		while os.path.exists(filepath) and i<max_ite:
			f,ext = os.path.splitex(filepath)
			filepath = f+str(i).zfill(int(math.log10(max_ite)))+'.'+ext
		tmp, ffs = os.path.split(filepath_start)
		tmp, ff  = os.path.split(filepath)

		r = QtWidgets.QMessageBox.question(self, "Rename files ?",
					"The file "+ ffs+" already exists. Change its name in "+\
					ff+"?",
					QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No|\
					QtWidgets.QMessageBox.Cancel)

		if r== QtWidgets.QMessageBox.Yes:
			return filepath
		elif r== QtWidgets.QMessageBox.No:
			return filepath_start
		else:
			return False


class FMZipFileManagement (FMTextFileManagement):
	@classmethod
	def splitZipfilepath(cls,filepath):
		""" Deals with path with the name ./foo.zip/foo1.txt

		Returns:
		⋅ If no zipfile can be found, returns False
		⋅ Otherwise, returns the tuple (zipfilepath,filename,inzip) with
			- zipfilepath : returns the zip filepath.
			- filename : the name of the file in the archive
			- inzip : True if the file is in the zipfile

		Examples:
		- './foo.zip/foo1.txt' with the zipfile 'foo.zip' existing and the
			file 'foo1.txt' in the zipfile existing:
			Returns ('foo.zip','foo1.txt',True)
		- './foo.zip/foo1.txt' with the zipfile 'foo.zip' existing and the
			file 'foo1.txt' not in the zipfile :
			Returns ('foo.zip','foo1.txt',False)
		- './foo.zip' with the zipfile 'foo.zip' existing:
			Returns ('foo.zip',None,False)
		- './foo.zip/foo1.txt' with the zipfile 'foo.zip' not existing:
			Returns False
		- './foo.txt' with the file 'foo.txt' not a zipfile:
			Returns False
		"""
		filepath = pathlib.Path(filepath)
		if zipfile.is_zipfile(str(filepath)):
			return (str(filepath),None,False)

		for zipfilepath in filepath.parents:
			if zipfile.is_zipfile(str(zipfilepath)):
				break
		else:
			return False

		filename = filepath.relative_to(zipfilepath)

		zipfilepath = str(zipfilepath)
		filename = str(filename)
		return (zipfilepath,filename,filename in cls.listFiles(zipfilepath))


	@classmethod
	def listFiles(cls,filepath):
		""" Will list all the files in the filepath.
		- filepath : the path of the file to open
		"""

		zfile = zipfile.ZipFile(filepath, 'r')
		try:
			result = zfile.namelist()  # We list all the files in the zip file
		finally:
			zfile.close()

		return result

	@classmethod
	def open(cls,zipfilepath,filename,with_codecs=True,output='read',mode='rU',encoding='utf-8'):
		"""
		- zipfilepath : the path of the zipfile to open
		- filename :  the name of the file to open inside the zipfile
		- with_codecs : if true, will give a utf-8 string
		- output : if output=='read' --> .read()
		           if output=='readlines' --> .readlines()
		- mode : the mode option in codecs.open function
		- encoding: the encoding option in codecs.open function
					(only if with_codecs is True)
		"""
		zipfilepath = str(zipfilepath) # if zipfilepath is a pathlib.Path

		zipfilepath = os.path.expanduser(zipfilepath)
		zf = zipfile.ZipFile(zipfilepath)

		try:
			data = zf.read(filename)
			if with_codecs:
				data = data.decode(encoding)

			if output=='readlines': # For some reason, zipfile does not have readlines methods
				data = data.split("\n")

			elif not output=='read':
				raise ValueError(
					"`output` parameter should be in {'read' or 'readlines'}"
					)
		finally:
			zf.close()

		return data

	@classmethod
	def save(cls,text,zipfilepath,filename,with_codecs=True,encoding='utf-8',
										modezip='a',ext=None):
		""" Function that will save the information contained in text into
		the file at filepath.
		- text: the unicode string to save into the path
		- zipfilepath: the path of the zip file
		- filename: the filename inside the zipfile
		- with_codecs : if True, will give a utf-8 string (or whatever is
			specified in encoding)
		- encoding: the encoding option in codecs.open function
			(only if with_codecs is True)
		- modezip : the open option of the zipfile ('w' or 'a')
		- ext: if not None, with ensure the extension (put the dot in front of
			the extension)
		"""
		zipfilepath = os.path.expanduser(str(zipfilepath))
		if ext != None and  os.path.splitext(filename)[1]!=ext:
			filename = os.path.splitext(filename)[0]+ext

		zf = zipfile.ZipFile(zipfilepath,mode=modezip)
		try :
			zf.writestr(filename, text)
		finally:
			zf.close()

		return True
