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

db.set_sqlDatabase(os.environ['NOMEN'])

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

cmds = []

cmds.append('select m._Nomen_key, m.symbol, m.name, m.statusNote, mgiID = a.accID ' + \
'into #nomen ' + \
'from MRK_Nomen m, ACC_Accession a ' + \
'where m._Marker_Status_key = 3 ' + \
'and m.submittedBy != "riken_autoload" ' + \
'and m._Nomen_key = a._Object_key ' + \
'and a._LogicalDB_Key = 1 ')

cmds.append('select n.*, a.accID ' + \
'from #nomen n, ACC_Accession a ' + \
'where n._Nomen_key *= a._Object_key ' + \
'and a._LogicalDB_Key != 1 ' + \
'order by n.symbol')

results = db.sql(cmds, 'auto')

prevNomen = ''
accids = []

for r in results[1]:

	if prevNomen != r['_Nomen_key']:

		if len(accids) > 0:
			fp.write(string.join(accids, ';') + CRT)
		elif prevNomen != '':
			fp.write(CRT)

		fp.write(r['mgiID'] + TAB)
		fp.write(r['symbol'] + TAB)
		fp.write(r['name'] + TAB)

		if r['statusNote'] != None:
			fp.write(regsub.gsub('\n', ' ', r['statusNote']))
		fp.write(TAB)

		prevNomen = r['_Nomen_key']
		accids = []
		
		if r['accID'] is not None and r['accID'] not in accids:
			accids.append(r['accID'])
	else:
		if r['accID'] is not None and r['accID'] not in accids:
			accids.append(r['accID'])

if len(accids) > 0:
	fp.write(string.join(accids, ';'))
fp.write(CRT)

reportlib.finish_nonps(fp)

