#!/usr/local/bin/python

'''
#
# MRK_NomenChrAberr.py 07/18/2001
#
# Report:
#       Chromosome aberrations associated with mutations with nomenclature changes
#
# Usage:
#       MRK_NomenChrAberr.py
#
#
#     From TR 2242:
#
#     These can be distinguished among markers by having type = cytogenetic marker;
#     and number of characters following the (xxx) is greater than 5. For these, 
#     the symbol to be verified is bounded on the left by the right partenthesis and 
#     on the right by a number. 
#
#     Example T(14;17)Tim2Lws -- the symbol Tim would be verified; 
#     and if not a current mouse symbol, added to the QC report.
#
# Notes:
#       - all reports use mgireport directory for output file
#       - all reports use db default of public login
#       - all reports use server/database default of environment
#       - use lowercase for all SQL commands (i.e. select not SELECT)
#       - all public SQL reports require the header and footer
#       - all private SQL reports require the header
#
# History:
#
# lec   07/16/2001
#       - created
#
'''

import sys
import os
import regsub
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

goodSymbols = []
badSymbols = []

#
# Main
#

def parseSymbol(symbol):

        [p1, p2] = string.splitfields(symbol, ')')

	print symbol + TAB + p2

	try:
        	[p3, p4] = string.splitfields(p2, '<')
	except:
        	[p3, p4] = regsub.split(p2, "[0-9]*")

	print p3	

        testSymbol = p3
	return testSymbol

def isCurrent(symbol, species = 1):

	ok = 0
	results = db.sql('select symbol, _Marker_Status_key from MRK_Marker ' + \
		'where _Species_key = %d ' % (species) + \
		'and symbol = "%s"' % (symbol), 'auto')
	for r in results:
		if r['symbol'] == symbol and \
		(r['_Marker_Status_key'] == 1 or r['_Marker_Status_key'] == -2):
			ok = 1

	return ok


fp = reportlib.init(sys.argv[0], 'Chromosomal Aberrations with nomenclature changes', os.environ['QCREPORTOUTPUTDIR'])

cmd = 'select symbol from MRK_Marker where _Marker_Type_key = 3 ' + \
	'and symbol like "%(%)[a-z]%[0-9]%" ' + \
	'order by symbol'

results = db.sql(cmd, 'auto')

for r in results:

	markerSymbol = r['symbol']
	testSymbol = parseSymbol(markerSymbol)

	if isCurrent(testSymbol):
		goodSymbols.append(markerSymbol)
	else:
		badSymbols.append(markerSymbol)

for s in goodSymbols:
	print s
print CRT

for s in badSymbols:
	print s
#	fp.write(s + CRT)

for s in badSymbols:
	fp.write(s + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)     # non-postscript file

