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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = 0)

db.sql('select m._Marker_key, m._Marker_Type_key, m.symbol, markerType = t.name ' + \
     'into #markers1 ' + \
     'from MRK_Marker m, MRK_Types t ' + \
     'where m._Organism_key = 1 ' + \
     'and m._Marker_Status_key in (1,3) ' + \
     'and m._Marker_Type_key = t._Marker_Type_key', None)

db.sql('create index idx1 on #markers1(_Marker_key)', None)

db.sql('select m1._Marker_key, m1.symbol, mgiID = a.accID, m1.markerType ' + \
     'into #markers2 ' + \
     'from #markers1 m1, ACC_Accession a ' + \
     'where m1._Marker_key = a._Object_key ' + \
     'and a._MGIType_key = 2 ' + \
     'and a.prefixPart = "MGI:" ' + \
     'and a._LogicalDB_key = 1 ' + \
     'and a.preferred = 1 ', None)

db.sql('create index idx1 on #markers2(_Marker_key)', None)

results = db.sql('select m.*, a.accID ' + \
	'from #markers2 m, MRK_History h, ACC_Accession a ' +
	'where m._Marker_key = h._Marker_key ' + \
	'and m._Marker_key = h._History_key ' + \
	'and h._Marker_Event_key = 1 ' + \
	'and h._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a.prefixPart = "J:" ' + \
        'and a._LogicalDB_key = 1 ' + \
        'order by m.symbol', 'auto')

for r in results:
	fp.write(r['mgiID'] + reportlib.TAB + \
	         r['symbol'] + reportlib.TAB + \
		 r['accID'] + reportlib.TAB + \
		 r['markerType'] + reportlib.CRT)

reportlib.finish_nonps(fp)

