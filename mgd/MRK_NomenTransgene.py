#!/usr/local/bin/python

'''
#
# MRK_NomenTransgene.py 07/16/2001
#
# Report:
#       Markers which are transgenes with nomenclature changes.
#
# Usage:
#       MRK_NomenTransgene.py
#
#
#     From TR 2242:
#
#     Markers which are transgenes can be distinguished amongst all markers in that their 
#     symbols begin with Tg and contain ().
#
#     [Note: there are currently a few exceptions, which need nomenclature updates].
#
#     For these, the following QC conditions apply. In each case the contents of the 
#     parentheses (xxx) is to be examined: 
#
#       1.If (xxx) contains no 'dash', no '/', and is not all CAPS;
#         then check if xxx is a current mouse symbol. If not, add to QC report. 
#         Example Tg(Zfp38)D1Hz -- the symbol Zfp38 would be verified. 
#
#       2.If (xxx) contains a 'dash', but no '/' and is not all CAPS;
#         examine the symbol preceding the dash to check if it is a current mouse symbol. 
#         If not, add to QC report. 
#         Example Tg(Wnt1-LacZ) -- the symbol Wnt1 would be verified. 
#
#       3.If (xxx) contains a '/', but no 'dash', the slash separates two gene symbols, ie, (xxx/yyy). 
#         If one or both of the xxx, yyy symbols are not all CAPS, 
#         then check the 'not all CAPS' symbols to see if
#         these are current mouse symbols. If not, add to QC report. 
#
#       4.If (xxx) is all CAPS; or if the symbol preceding a 'dash' is all CAPS; 
#         or if one or both of the symbols in
#         (xxx/yyy) is all CAPS, check current human symbols to verify. 
#         If not a current human symbol, add to QC #         report. 
#         Example Tg(TCF3/HLF)1Mlc -- there are 2 gene symbols TCF3 and HLF, both all CAPS and therefore
#         would be verified against current human symbols. 
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

	# too complicated; just ignore it
	if string.count(symbol, '(') > 1:
	    return symbol

        [p1, p2] = string.splitfields(symbol, '(')
        [p3, p4] = string.splitfields(p2, ')')
        testSymbol = p3
	return testSymbol

def isAllCaps(symbol):

	ok = 1
	for i in range (len(symbol)):
		if symbol[i] not in string.uppercase and symbol[i] not in string.digits:
			ok = 0

	return ok

def isCurrent(symbol, organism = 1):

	ok = 0
	results = db.sql('select symbol, _Marker_Status_key from MRK_Marker ' + \
		'where _Organism_key = %d ' % (organism) + \
		'and symbol = "%s"' % (symbol), 'auto')
	for r in results:
		if r['symbol'] == symbol and r['_Marker_Status_key'] in [-2,1,3]:
			ok = 1

	return ok


fp = reportlib.init(sys.argv[0], 'Transgenes with nomenclature changes', os.environ['QCREPORTOUTPUTDIR'])

cmd = 'select symbol from MRK_Marker where symbol like "Tg(%" ' + \
	'and symbol not like "Tg(%-%)%" ' + \
	'and symbol not like "Tg(%/%)%" ' + \
	'order by symbol'

results = db.sql(cmd, 'auto')

for r in results:

	markerSymbol = r['symbol']
	testSymbol = parseSymbol(markerSymbol)

	if isAllCaps(testSymbol):
		organism = 2
	else:
		organism = 1

	if isCurrent(testSymbol, organism):
		goodSymbols.append(markerSymbol)
	else:
		badSymbols.append(markerSymbol)

cmd = 'select symbol from MRK_Marker where symbol like "Tg(%" ' + \
	'and symbol like "Tg(%-%)%" ' + \
	'and symbol not like "Tg(%/%)%" ' + \
	'order by symbol'

results = db.sql(cmd, 'auto')

for r in results:

	markerSymbol = r['symbol']
	testSymbol = parseSymbol(markerSymbol)

	try:
		[s1, s2] = string.splitfields(testSymbol, '-')

		if isAllCaps(s1):
			organism = 2
		else:
			organism = 1
	
		if isCurrent(s1, organism):
			goodSymbols.append(markerSymbol)
		else:
			badSymbols.append(markerSymbol)

	except:
		pass

cmd = 'select symbol from MRK_Marker where symbol like "Tg(%" ' + \
	'and symbol not like "Tg(%-%)%" ' + \
	'and symbol like "Tg(%/%)%" ' + \
	'order by symbol'

results = db.sql(cmd, 'auto')

for r in results:

	markerSymbol = r['symbol']
	testSymbol = parseSymbol(markerSymbol)

	try:
		[s1, s2] = string.splitfields(testSymbol, '/')

		if isAllCaps(s1):
			organism1 = 2
		else:
			organism1 = 1

		if isAllCaps(s2):
			organism2 = 2
		else:
			organism2 = 1

		if isCurrent(s1, organism1) and isCurrent(s2, organism2):
			goodSymbols.append(markerSymbol)
		else:
			badSymbols.append(markerSymbol)

	except:
		pass

for s in badSymbols:
	fp.write(s + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)     # non-postscript file

