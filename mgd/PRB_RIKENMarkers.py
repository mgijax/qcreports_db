#!/usr/local/bin/python

'''
#
# PRB_RIKENMarkers.py 11/16/2001 (TR 3100)
#
# Report:
#	TR 3100
#       Tab-delimited file
#
#	RIKEN Clone ID
#	MGI Marker ID
#	DDBJ ID
#	Marker/Clone relationship
# Usage:
#       PRB_RIKENMarkers.py
#
# Used by:
#       MGI Curatorial Group (Sophia)
#
# Notes:
#
# History:
#
# lec	11/16/2001
#	- new
#
'''
 
import sys
import os
import string
import db
import reportlib

#
# Main
#

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fp.write('RIKEN Clone ID' + reportlib.TAB)
fp.write('R' + reportlib.TAB)
fp.write('Marker ID' + reportlib.TAB)
fp.write('GenBank ID' + reportlib.CRT)

# Get all RIKEN Clones w/ Marker relationships

cmds = []
cmds.append('select pm._Probe_key, pm._Marker_key, pm.relationship ' + \
	'into #riken ' + \
	'from PRB_Probe p, PRB_Marker pm ' + \
	'where p.name like "RIKEN%" ' + \
	'and p._Probe_key = pm._Probe_key')
cmds.append('create index idx1 on #riken(_Probe_key)')
cmds.append('create index idx2 on #riken(relationship)')
db.sql(cmds, None)

# Get GenBank IDs
results = db.sql('select r._Probe_key, a.accID ' + \
	'from #riken r, ACC_Accession a ' + \
	'where r._Probe_key = a._Object_key ' + \
	'and a._MGIType_key = 3 ' + \
	'and a._LogicalDB_Key = 9 ', 'auto')
gbIDs = {}
for r in results:
    key = r['_Probe_key']
    value = r['accID']
    if not gbIDs.has_key(key):
	gbIDs[key] = []
    gbIDs[key].append(value)

cmds = []
cmds.append('select r._Probe_key, r.relationship, a1.accID, markerID = a2.accID ' + \
	'into #riken2 ' + \
	'from #riken r, ACC_Accession a1, ACC_Accession a2 ' + \
	'where r._Probe_key = a1._Object_key ' + \
	'and a1._MGIType_key = 3 ' + \
	'and a1._LogicalDB_Key = 26 ' + \
	'and r._Marker_key = a2._Object_key ' + \
	'and a2._MGIType_key = 2 ' + \
	'and a2.prefixPart = "MGI:" ' + \
	'and a2._LogicalDB_key = 1 ' + \
	'and a2.preferred = 1 ')
cmds.append('create index idx1 on #riken2(relationship)')
cmds.append('create index idx2 on #riken2(accID)')')
db.sql(cmds, None)

results = db.sql('select _Probe_key, relationship, accID, markerID ' + \
	'from #riken2 ' + \
	'order by relationship, accID', 'auto')

for r in results:

	key = r['_Probe_key']

	if r['relationship'] == None:
	    relationship = "NULL"
	else:
	    relationship = r['relationship']

	if not gbIDs.has_key(key):
		fp.write(r['accID'] + reportlib.TAB + \
		         r['relationship'] + reportlib.TAB + \
		         r['markerID'] + reportlib.TAB + \
		         "NULL" + reportlib.CRT)
	else:
	    for g in gbIDs[key]:
		fp.write(r['accID'] + reportlib.TAB + \
		         r['relationship'] + reportlib.TAB + \
		         r['markerID'] + reportlib.TAB + \
		         g + reportlib.CRT)

reportlib.finish_nonps(fp)
db.useOneConnection(0)
