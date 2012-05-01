#!/usr/local/bin/python

'''
#
# NOMEN_Reserved.py
#
# Report:
#       TR 1872
#	Nomen Reserved Symbols for Hes Wain (HUGO Human Nomenclature Committee)
#
# Usage:
#       NOMEN_Reserved.py
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
# lec	02/03/2005
#	- TR 6547
#
# lec	08/10/2000
#	- created
#
'''
 
import sys 
import os
import string
import db
import mgi_utils
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

db.sql('select m._Nomen_key, m.symbol, m.name, m.statusNote, mgiID = a.accID, ' + \
	'cdate = convert(char(10), m.creation_date, 101) ' + \
	'into #nomen ' + \
	'from NOM_Marker_View m, ACC_Accession a ' + \
	'where m.status = "Reserved" ' + \
	'and m._Nomen_key = a._Object_key ' + \
	'and a._MGIType_key = 21 ' + \
	'and a._LogicalDB_Key = 1 ', None)

db.sql('create index idx1 on #nomen(_Nomen_key)', None)

results = db.sql('select n._Nomen_key, a.accID ' + \
	'from #nomen n, ACC_Accession a ' + \
	'where n._Nomen_key = a._Object_key ' + \
	'and a._MGIType_key = 21 ' + \
	'and a._LogicalDB_Key != 1 ', 'auto')

accids = {}
for r in results:
    key = r['_Nomen_key']
    value = r['accID']
    if not accids.has_key(key):
	accids[key] = []
    accids[key].append(value)

fp.write('MGI ID' + TAB)
fp.write('Symbol' + TAB)
fp.write('Name' + TAB)
fp.write('Details' + TAB + TAB)
fp.write('Reserved Date' + 2*CRT)

results = db.sql('select * from #nomen order by symbol', 'auto')
for r in results:

	fp.write(r['mgiID'] + TAB)
	fp.write(r['symbol'] + TAB)
	fp.write(r['name'] + TAB)

	if r['statusNote'] != None:
		fp.write(string.replace(r['statusNote'], '\n', ' '))
	fp.write(TAB)

	if accids.has_key(r['_Nomen_key']):
		fp.write(string.join(accids[r['_Nomen_key']], ';'))
	fp.write(TAB)

	fp.write(r['cdate'] + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

