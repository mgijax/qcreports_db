#!/usr/local/bin/python

'''
#
# ALL_NomenText.py
#
# Report:
#
# Usage:
#       ALL_NomenText.py
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
# lec   08/23/2004
#       - created
#
'''

import sys
import os
import string
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

reportHeader = 'Symbols which have undergone withdrawals and appear in Allele Molecular Notes' + CRT + \
	'Nomenclature Event Date: %s' % (mgi_utils.date('%m/%Y'))

fp = reportlib.init(sys.argv[0], reportHeader, os.environ['QCREPORTOUTPUTDIR'])

fp.write(string.ljust('Allele Symbol', 32))
fp.write(string.ljust('Old Symbol', 32))
fp.write(string.ljust('New Symbol', 32))
fp.write(string.ljust('Event Date', 10) + CRT)
fp.write(string.ljust('-------------', 32))
fp.write(string.ljust('----------', 32))
fp.write(string.ljust('----------', 32))
fp.write(string.ljust('----------' ,10) + CRT*2)

cmds = []

# all Allele Molecular Notes

cmds.append('select n.note, n._Allele_key, a.symbol ' + \
	'from ALL_Note_Molecular_View n, ALL_Allele a ' + \
	'where n._Allele_key = a._Allele_key ' + \
	'order by _Allele_key')

# All symbols w/ nomenclature change in the last month

cmds.append('select distinct h._History_key, event_date = convert(char(10), h.event_date, 101), r.symbol, r.current_symbol ' + \
	'from MRK_History h, MRK_Current_View r ' + \
	'where datepart(mm, h.event_date) = datepart(mm, getdate()) ' + \
	'and datepart(yy, h.event_date) = datepart(yy, getdate()) ' + \
	'and h._Marker_Event_key in (2,3,4,5) ' + \
	'and h._History_key = r._Marker_key ' + \
	'order by event_date desc')

results = db.sql(cmds, 'auto')

notes1 = {}
alleles = {}
for r in results[0]:
    key = r['_Allele_key']
    value = r['note']
    if not notes1.has_key(key):
	notes1[key] = []
    notes1[key].append(value)

    if not alleles.has_key(key):
        alleles[key] = r['symbol']

notes2 = {}
for r in notes1.keys():
    notes2[r] = string.join(notes1[r], '')

for r in results[1]:
	for n in notes2.keys():
	    searchNote = notes2[n]
	    searchSymbol = ' ' + r['symbol'] + ' '
	    if string.find(searchNote, searchSymbol) >= 0:
		fp.write(string.ljust(alleles[n], 32) + 
		         string.ljust(r['symbol'], 32) + 
		         string.ljust(r['current_symbol'], 32) + 
		         string.ljust(r['event_date'], 10) + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)     # non-postscript file

