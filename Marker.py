#!/usr/local/bin/python

'''
#
# Marker.py 11/16/98
#
# Report:
#	Basic Marker info
#
# Usage:
#       Marker.py
#
# Generated from:
#       Editing Interface Marker Form
#
# Notes:
#
# History:
#
# lec	01/13/98
#	- added comments section
#	- output file name contains first Marker symbol
#
'''
 
import sys
import os
import string
import mgdlib
import reportlib

CRT = reportlib.CRT
fp = None

def printHeader():

	fp.write(string.ljust('Symbol', 20))
	fp.write(string.ljust('Chr', 8))
	fp.write(string.ljust('Offset', 8))
	fp.write(string.ljust('Name', 30))
	fp.write(CRT)

	fp.write(string.ljust('------', 20))
	fp.write(string.ljust('---', 8))
	fp.write(string.ljust('------', 8))
	fp.write(string.ljust('----', 30))
	fp.write(2*CRT)

results = mgdlib.sql(sys.argv[1], 'auto')

for r in results:

	command = 'select symbol, chromosome, name = substring(name, 1, 50), offset ' + \
		  'from MRK_Mouse_View where _Marker_key = ' + `r['_Marker_key']`
	markers = mgdlib.sql(command, 'auto')

	for m in markers:
		if fp is None:  
			reportName = 'Marker.%s.rpt' % m['symbol']
			fp = reportlib.init(reportName, 'Markers', os.environ['QCREPORTOUTPUTDIR'])
			printHeader()

		fp.write(string.ljust(m['symbol'], 20))
		fp.write(string.ljust(m['chromosome'], 8))
		fp.write(string.ljust(mgdlib.prvalue(m['offset']), 8))
		fp.write(string.ljust(m['name'], 30))
		fp.write(CRT)

reportlib.finish_nonps(fp)

