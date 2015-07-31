#!/usr/bin/python
'''\nSQL Plus Report Generator
Usage: python makereport.py -i <sql_file>"
Arguments:
 -i, --input      sql input file
 -o, --output	  html output file (report)
 -c, --connection connection string to connect to the database
 -t, --template   template file
 --title		  report title
Flags:
 -h, --help       help
'''

from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader
import logging
import tempfile
import sys, os
import getopt

inputFileName = ''
connectString = ''
outputFileName = 'report_output.html'
templateFileName = 'template.html'
title = 'Report'
sql = False

def usage():
	print(__doc__)
	sys.exit(0)

try:
	options, remainder = getopt.gnu_getopt(sys.argv[1:],
			'o:i:c:t:h', ['output=',
                      'input=',
				      'connection=',
				      'template=',
				      'help',
				      'title='])
except getopt.GetoptError as err:
	usage()
	sys.exit(2)

if (not os.path.isfile(inputFileName)):
	usage()
	sys.exit(2)

for opt, arg in options:
	if opt in ('-o', '--output'):
		outputFileName = arg
	elif opt in ('-i', '--input'):
		inputFileName = arg
	elif opt in ('-c', '--connection'):
		connectString = arg
	elif opt in ('-t', '--template'):
		templateFileName = arg
	elif opt in ('-h', '--help'):
		usage()
	elif opt == '--title':
		title = arg

logging.info("Creating reports...")

dirname, basename = os.path.split(inputFileName)
fileTemp = tempfile.NamedTemporaryFile(delete = False, dir = dirname, suffix='.LST')
fileTempName = fileTemp.name
fileTemp.close()

session = Popen(['sqlplus', '-S', connectString], stdin=PIPE, stdout=PIPE, stderr=PIPE)

session.stdin.write(bytes('SET PAGESIZE 50000\n', 'UTF-8'))
session.stdin.write(bytes('SET MARKUP HTML ON TABLE "class=detail cellspacing=0" ENTMAP OFF\n', 'UTF-8'))
session.stdin.write(bytes('SET FEEDBACK OFF\n', 'UTF-8'))
session.stdin.write(bytes('SET TERMOUT OFF\n', 'UTF-8'))
session.stdin.write(bytes('SPOOL ' + fileTempName + '\n', 'UTF-8'))
session.stdin.write(bytes('start ' + inputFileName + '\n', 'UTF-8'))
session.stdin.write(bytes('SPOOL OFF\n', 'UTF-8'))
session.stdin.write(bytes('SET MARKUP HTML OFF\n', 'UTF-8'))

queryResult, errorMessage = session.communicate()

if errorMessage:
	logging.error(errorMessage)
	sys.exit(1)

logging.info("Templating...")

templateFileDir = os.path.dirname(os.path.abspath(templateFileName))
templateLoader = FileSystemLoader(templateFileDir)
templateEnv = Environment(loader=templateLoader)
sqlContent = open(inputFileName, 'r').read()
dataContent = open(fileTempName, 'r').read()
context = {'title' : title, 'sql' : sqlContent, 'data' : dataContent}

with open(outputFileName, 'w') as f:
    html = templateEnv.get_template(templateFileName).render(context)
    f.write(html)

os.remove(fileTempName)
