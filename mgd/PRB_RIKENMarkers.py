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
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmds = []

# Get all RIKEN Clones w/ Marker relationships
cmds.append('select distinct pm._Probe_key, pm._Marker_key, pm.relationship ' + \
'into #riken ' + \
'from PRB_Probe p, PRB_Marker pm ' + \
'where p.name like "RIKEN%" ' + \
'and p._Probe_key = pm._Probe_key')

# Get DDBJ IDs
cmds.append('select r.*, ddbjID = a.accID ' + \
'into #final ' + \
'from #riken r, ACC_Accession a ' + \
'where r._Probe_key = a._Object_key ' + \
'and a._MGIType_key = 3 ' + \
'and a._LogicalDB_Key = 9 ' + \
'union ' + \
'select r.*, NULL ' + \
'from #riken r ' + \
'where not exists (select 1 from ACC_Accession a ' + \
'where r._Probe_key = a._Object_key ' + \
'and a._MGIType_key = 3 ' + \
'and a._LogicalDB_Key = 9)')

cmds.append('select a1.accID, markerID = a2.accID, f.ddbjID, f.relationship ' + \
'from #final f, ACC_Accession a1, ACC_Accession a2 ' + \
'where f._Probe_key = a1._Object_key ' + \
'and a1._MGIType_key = 3 ' + \
'and a1._LogicalDB_Key = 26 ' + \
'and f._Marker_key = a2._Object_key ' + \
'and a2._MGIType_key = 2 ' + \
'and a2.prefixPart = "MGI:" ' + \
'and a2._LogicalDB_key = 1 ' + \
'and a2.preferred = 1 ' + \
'order by f.relationship, a1.accID')

results = db.sql(cmds, 'auto')

fp.write('RIKEN Clone ID' + reportlib.TAB)
fp.write('R' + reportlib.TAB)
fp.write('Marker ID' + reportlib.TAB)
fp.write('DDBJ ID' + reportlib.CRT)

for r in results[-1]:
	fp.write(r['accID'] + reportlib.TAB)

	if r['relationship'] == None:
		fp.write("NULL" + reportlib.TAB)
	else:
		fp.write(r['relationship'] + reportlib.TAB)

	fp.write(r['markerID'] + reportlib.TAB)

	if r['ddbjID'] == None:
		fp.write("NULL" + reportlib.CRT)
	else:
		fp.write(mgi_utils.prvalue(r['ddbjID']) + reportlib.CRT)

reportlib.finish_nonps(fp)

