#!/usr/local/bin/python

'''
#
# NomenSearch.py 08/11/1999
#
# Report:
#	Basic Nomen info
#
# Usage:
#       NomenSearch.py
#
# Generated from:
#       Editing Interface Nomenclature Form
#
# Notes:
#
# History:
#
# lec	08/11/1999
#	- created
#
'''
 
import sys
import os
import string
import mgdlib
import reportlib

CRT = reportlib.CRT
fp = None
records = 0

def printHeader():

	fp.write('Search Parameters:  ')
	fp.write(CRT + printSelect + CRT*2)

	fp.write(string.ljust('Symbol', 25))
	fp.write(CRT)

	fp.write(string.ljust('------', 20))
	fp.write(2*CRT)

cmd = sys.argv[1]
printSelect = sys.argv[2]
results = mgdlib.sql(cmd, 'auto')

for r in results:

	if fp is None:  
		reportName = 'NomenSearch.%s.rpt' % r['approvedSymbol']
		fp = reportlib.init(reportName, 'Nomenclature Search Results', os.environ['QCREPORTOUTPUTDIR'])
		printHeader()

	fp.write(string.ljust(r['approvedSymbol'], 25))
	fp.write(CRT)
	records = records + 1

fp.write(2*CRT + '(' + `records` + ' rows affected)' + CRT)
reportlib.finish_nonps(fp)

