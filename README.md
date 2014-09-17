Usage with QtGui interface:
	>>>athenawriter [options] [documents]
Usage in console mode:
	>>>athenawriter --console [options] [documents]
	
Options:
--help or -h						
	Show this message.
--import <import-options>			
	Import the document from a different format.
	For more information, use:
	>>>athenawriter --import --help
	Note: will make importation if the document is not a .athw
--export <export-options>
	Export the document from a different format.
	For more information, use:
	>>>athenawriter --export --help
--import_export:
	Import the document from a format and export it in another
--clean <n>
	Will clean the file when openning it 'n' times (by default n=1)
--examples
	Will show examples of how to use the command line
--language
	To change the language of the AthenaWriter
	To have the language list, do :
	>>>athenawriter --language --help

Examples :
Show this text:
>>athenawriter --examples

Open ./example.athw:
>>>athenawriter ./example.athw

Open ./example.athw and clean the file as it opens:
>>>athenawriter --clean ./example.athw

Convert ./example.odt in ./example.athw and open it in a 
AthenaWriter window:
>>>athenawriter --import ./example.odt

Convert ./example.odt in ./example.athw, open it in a 
AthenaWriter window and cleaning the file as it opens:
>>>athenawriter --import --clean ./example.odt

Convert ./example.odt in ./example.athw and open without 
opening it in a AthenaWriter window:
>>>athenawriter --console --import ./example.odt

Convert ./example.athw in ./example.html:
>>>athenawriter --export html ./example.odt
Note: here the --console mode is automatic

Convert ./example.odt in ./otherdir/example.html:
>>>athenawriter --export html --outdir ./otherdir/ ./example.odt
Note: here the --console mode is automatic



