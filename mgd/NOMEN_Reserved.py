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
# lec	08/10/2000
#	- created
#
'''
 
import sys 
import os
import string
import regsub
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = 0)

cmds = []

cmds.append('select m._Nomen_key, m.symbol, m.name, m.statusNote, mgiID = a.accID ' + \
'into #nomen ' + \
'from NOM_Marker_View m, ACC_Accession a ' + \
'where m.status = "Reserved" ' + \
'and m._Nomen_key = a._Object_key ' + \
'and a._MGIType_key = 21 ' + \
'and a._LogicalDB_Key = 1 ')

cmds.append('select n._Nomen_key, a.accID ' + \
'from #nomen n, ACC_Accession a ' + \
'where n._Nomen_key = a._Object_key ' + \
'and a._MGIType_key = 21 ' + \
'and a._LogicalDB_Key != 1 ')

cmds.append('select * from #nomen order by symbol')

results = db.sql(cmds, 'auto')

accids = {}
for r in results[1]:
    key = r['_Nomen_key']
    value = r['accID']
    if not accids.has_key(key):
	accids[key] = []
    accids[key].append(value)

for r in results[2]:

	fp.write(r['mgiID'] + TAB)
	fp.write(r['symbol'] + TAB)
	fp.write(r['name'] + TAB)

	if r['statusNote'] != None:
		fp.write(regsub.gsub('\n', ' ', r['statusNote']))
	fp.write(TAB)

	if accids.has_key(r['_Nomen_key']):
		fp.write(string.join(accids[r['_Nomen_key']], ';'))
	fp.write(CRT)

reportlib.finish_nonps(fp)

