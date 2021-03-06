from PyQt5 import QtGui, QtCore, QtWidgets
from AthenaWriterCore import __version__,AWCore,AWAbout
from AthenaWriterMainWindow import AWWriterText
from DocExport.DocExport import DEList
from DocImport.DocImport import DIList

import argparse
import re
import sys
import os

class AWConsoleError (Exception):
    def __init__(self,raison):
        self.raison = raison

    def __str__(self):
        return self.raison.encode('ascii','replace')


class AWConsole (AWCore):
	"""
	Will be the console version of the software, it uses the function
	contained in AWCore to open, save, export etc. the files
	"""
	def __init__(self):
		AWCore.__init__(self)
		self.argv =	sys.argv

		self.parser = argparse.ArgumentParser()

		self.parser.add_argument("--console",
			help="Execute in console mode",
			action="store_true")

		self.parser.add_argument("file",
			help="File to execute",
			nargs='?')

		self.parser.add_argument("--import",
			help="Import a file, for its the options, read the documentation",
			nargs='+',
			dest='importt')

		self.parser.add_argument("--export",
			help="Export a file",
			nargs='+',
			metavar="export_options")

		self.parser.add_argument("--recheck",
			help="Recheck the typography when opening the file.",
			action="store_true")

		for i in range(1,10):
			self.parser.add_argument("-"+str(i),
				help="Will load the "+str(i)+"-th last files in the "+\
														"LastFile.txt list",
				action="store_true",
				dest="last_file_"+str(i)
				)

		self.parser.add_argument("-l","--list_last_files",
			help="Will list the last files of LastFile.txt",
			dest='list_last_files',action="store_true")

		self.parser.add_argument("--about",
			help="Print the description of the software",
			dest='about',action="store_true")

		self.parser.add_argument("-v","--version",
			help="Will print the current version of the software",
			dest='version',action="store_true")

		self.args = self.parser.parse_args()

		l = [i for i in range(1,10) if self.args.__dict__["last_file_"+str(i)]]
		if len(l)>1:
			raise AWConsoleError("Several last files oppening option "+\
											"specified; please use only one.")
		elif len(l)==1 :
			self.args.last_file = l[0]
		else : self.args.last_file = False


		if self.args.last_file:
			if self.args.file!=None:
				raise AWConsoleError("Do not use the '-1' argument if a file"+\
						"is specified.")
			if len(self.lastFiles.getValues())==0:
				raise AWConsoleError("The last files memory is empty can not"+\
						"open the last of the list.")

			self.args.file=self.lastFiles.getValues()[self.args.last_file-1]

		if self.args.importt!=None or self.args.export!=None:
			if self.args.last_file :
				raise AWConsoleError("Please specify all the files, do not "+\
						"use the '-1' argument.")

			else :
				self.args.file = sys.argv[-1]
		# self.print_args()


	def print_args(self):

		"""For debugging reasons"""
		print('self.args.console',self.args.console,type(self.args.console))
		print('self.args.file',self.args.file,type(self.args.file))
		print('self.args.importt',self.args.importt,type(self.args.importt))
		print('self.args.export',self.args.export,type(self.args.export))
		print('self.args.outdir',self.args.outdir,type(self.args.outdir))
		print('self.args.recheck',self.args.recheck,type(self.args.recheck))
		print('self.args.last_file',self.args.last_file,type(self.args.last_file))
		print('self.args.l',self.args.l,type(self.args.l))



	def get_sub_options(self,arg_list):
		"""
		Return a dictionnary based on the arg_list that were written under the
		form of :
		KEY=VALUE
		"""
		res={}
		if arg_list!=None:
			for i,kv in enumerate(arg_list):
				list_kv = kv.split('=')
				if len(list_kv)!=2:
					if i!=len(arg_list)-1:
						# if it has a wrong spelling and it is not the last
						# option
						raise AWConsoleError('The options should be under "+\
													the form of KEY=VALUE.')
				else:

					res[list_kv[0]]=list_kv[1].decode('utf-8')
		return res

	def perfomImportOptions(self):
		"""
		Will compute the options for the importation mode: in particular, it is
		useful to compte the lines we have to skip in the file.
		"""
		arg_dict = self.get_sub_options(self.args.importt)
		for k,v in list(arg_dict.items()):
			if k == 'skip_lines':
				to_skip=[]
				list_fig=v.split(';')
				for val in list_fig:
					A = re.match('^(-?[0-9]+)-(-?[0-9]+)$',val)
					if A!=None:
						to_skip+=list(range(int(A.group()[0]),int(A.group()[1])))
					elif re.match('^[0-9]+$',val)!=None:
						to_skip+=[int(val)]
					else:
						self.parser.error(
							"The skip_lines option should be numbers "+\
							"separated by ';' or '-' for different ranges" )
				return to_skip

			else:
				self.parser.error(
					"Unknown option name for --import options, should be "+\
					"in : [skip_lines]")




	def perfom_command(self):
		if self.args.export: # if we export the file, the console mode is
							# automatic
			self.args.console=True

		########################### list last files ###########################
		if self.args.list_last_files:# if we export the file, the console mode
							# is disabled
			self.args.console = True

			lf = self.lastFiles.getValues()
			if len(lf)>9: lf = lf[:9]
			print("=== Last files list ===")
			print('\n'.join([str(i+1)+'- '+v for i,v in enumerate(lf)]))

		self.filepath = self.args.file
		############# importation #############
		if self.args.importt :
			if self.args.file==None :
				raise AWConsoleError('Please specify the file to import.')
			path,e = os.path.splitext(self.args.file)
			e = e[1:]#the [1:] is to skip the dot in the extension

			# We import the file
			to_skip = self.perfomImportOptions()
			self.CMD_FileImport(
				filepath = self.args.file,
				format_name = e,
				to_skip = to_skip)

			# We recheck the typography whenether it is needed
			if self.args.recheck :
				self.textEdit.actionRecheckTypography.triggered()

			# We determine what should be the output path for the file
			arg_dict = self.get_sub_options(self.args.importt)

			if 'filepath' in arg_dict:
				filepath = arg_dict['filepath']
			else :
				filepath,ext = os.path.splitext(self.args.file)
				filepath += '.athw'

			if 'outdir' in arg_dict:
				dir,filepath = os.path.split(filepath)
				filepath = os.path.join(arg_dict['outdir'],filepath)

			# We save the file
			self.CMD_FileSave(filepath = filepath)



			# fiimport_instance = FIList[list_extentions.index(e)](file=self.args.file)
			# fiimport_instance.import2xml()
			# self.perfomImportOptions(fiimport_instance)

			# newfile = fiimport_instance.save_file(**arguments)
			# self.args.file = newfile

		############### exportation ###############
		if self.args.export :
			# import TextEdit.TextEditFormats

			if self.args.file==None :
				raise AWConsoleError('Please specify the file to export.')
			export_args = self.get_sub_options(self.args.export)
			if 'format' not in export_args:
				raise AWConsoleError(
					'You should give the format of exportation.\n'+\
					'Example : format=txt')
			format = export_args.pop('format')

			# We open the .athw file
			self.CMD_FileOpen(filepath = self.args.file)

			# We recheck the typography whenether it is needed
			if self.args.recheck :
				self.textEdit.actionRecheckTypography.trigger()

			# We determine what should be the output path for the file
			if 'filepath' in export_args:
				filepath = export_args.pop('filepath')
			else :
				filepath,ext = os.path.splitext(self.args.file)
				filepath += '.'+format

			if 'outdir' in export_args:
				dir,filepath = os.path.split(filepath)
				filepath = os.path.join(export_args['outdir'],filepath)

			# We export the file
			self.CMD_FileExport(format_name=format,filepath=filepath,
																**export_args)


#
#			xml_string = FMTextFileManagement.open(self.args.file)
#
#			feexport_instance = FEList[list_extentions.index(format)](\
#									textedit_formats=TextEdit.TextEditFormats)
#			# export_string = feexport_instance.export(xml_string = xml_string,**export_args)
#			feexport_instance.export(xml_string = xml_string,**export_args)
#				# export the file with the arguments in export_args
#			if filepath==None:
#				export_filename,e = os.path.splitext(self.args.file)
#				export_filename += '.'+ format
#			else:
#				export_filename = filepath
#
#			if outdir!=None:
#				e,export_filename=os.path.split(export_filename)
#				export_filename = os.path.join(outdir,export_filename)
#
#			feexport_instance.export_file(dest_file=export_filename)
#
#
		if not self.args.console:
			# app = QtWidgets.QApplication(sys.argv)
			writerText = AWWriterText()
			if self.filepath !=None :
				writerText.SLOT_actionFileOpen(filepath=self.filepath)
			# writerText.show()
			return writerText
			# sys.exit(writerText.exec_())
		if self.args.version:
			print("Version : ",__version__)
		if self.args.about:
			print("".join(["="]*50))
			print(AWAbout)
			print("".join(["="]*50))
		return None


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	cons = AWConsole()
	writerText = cons.perfom_command()
	if writerText!=None:
		dir,f = os.path.split(__file__)
		iconpath = os.path.join(dir,'./Images/LogoTmp.png')
		app.setWindowIcon(QtGui.QIcon(iconpath))
		writerText.show()
		sys.exit(app.exec_())
	else:
		app.closeAllWindows()
