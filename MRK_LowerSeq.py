#!/usr/local/bin/python

'''
#
# MRK_LowerSeq.py
#
# Report:
#       TR 1462
#	Identify all the gene symbols in the database that start with a 
#	lower case symbol (these should be phenotypic mutants) that have a a Genbank 
#	sequence link.  
#
# Usage:
#       template.py
#
# Notes:
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	03/23/2000
#	- created
#
'''
 
import sys 
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Lowercase Gene Symbols which have GenBank IDs', os.environ['QCREPORTOUTPUTDIR'])

fp.write('%-25s' % 'Symbol' + TAB)
fp.write('%-30s' % 'GenBankID' + CRT)
fp.write('%-25s' % '------' + TAB)
fp.write('%-30s' % '---------' + CRT)

cmd = 'select m.symbol, a.accID ' + \
'from MRK_Marker m, MRK_Acc_View a ' + \
'where m._Species_key = 1 ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._LogicalDB_key = 9 ' + \
'order by m.symbol'

results = db.sql(cmd, 'auto')

for r in results:
	ok = 1
	for i in range (len(r['symbol']) - 1):
		if r['symbol'][i] not in string.lowercase:
			ok = 0

	if ok:
		fp.write('%-25s' % r['symbol'] + TAB)
		fp.write('%-30s' % r['accID'] + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)	# non-postscript file
