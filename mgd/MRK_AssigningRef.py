#!/usr/local/bin/python

'''
#
# MRK_AssigningRef.py 02/25/2002
# TR 3386
#
# Report:
#       Tab-delimited file of current Mouse Markers
#	1. MGI Acc ID
#	2. Symbol
#	3. Assigning Reference (J:####)
#	4. Marker Type
#
# Usage:
#       MRK_AssigningRef.py
#
# Used by:
#	Sophia
#
# Notes:
#
# History:
#
# lec	02/25/2002
#	- added comments
#
'''

import sys
import os
import db
import reportlib

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

cmds = []

cmds.append('select m._Marker_key, m.symbol, mgiID = a.accID, markerType = t.name ' + \
     'into #markers ' + \
     'from MRK_Marker m, ACC_Accession a, MRK_Types t ' + \
     'where m._Species_key = 1 ' + \
     'and m._Marker_Status_key in (1,3)' + \
     'and m._Marker_key = a._Object_key ' + \
     'and a._MGIType_key = 2 ' + \
     'and a.prefixPart = "MGI:" ' + \
     'and a._LogicalDB_key = 1 ' + \
     'and a.preferred = 1 ' + \
     'and m._Marker_Type_key = t._Marker_Type_key')

cmds.append('create unique clustered index index_marker_key on #markers(_Marker_key)')

cmds.append('select m.*, a.accID ' + \
	'from #markers m, MRK_History h, ACC_Accession a ' +
	'where m._Marker_key = h._Marker_key ' + \
	'and m._Marker_key = h._History_key ' + \
	'and h._Marker_Event_key = 1 ' + \
	'and h._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a.prefixPart = "J:" ' + \
        'and a._LogicalDB_key = 1 ' + \
        'order by m.symbol')

results = db.sql(cmds, 'auto')

for r in results[2]:
	fp.write(r['mgiID'] + reportlib.TAB + \
	         r['symbol'] + reportlib.TAB + \
		 r['accID'] + reportlib.TAB + \
		 r['markerType'] + reportlib.CRT)

reportlib.finish_nonps(fp)

