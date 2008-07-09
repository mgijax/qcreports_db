#!/usr/local/bin/python

'''
#
# GO_gp2protein_SWP_TR.py
#       (TR 6942, special MGI version, TR 4877, originally TR 3659)
#
# Report:
#       Tab-delimited file
#
# Usage:
#       GO_gp2protein_SWP_TR.py
#
# Output
#
#	A tab-delimited file in this format:
#	field 1: MGI Marker ID
#	field 2: SWP:#####;SWP:#####;...
# Used by:
#
#	Harold
#
# Notes:
#
# History:
#
# 08/01/2005	lec
#	- TR 6942; special version for Harold; include SP and TrEMBL
#
#	Created for TR3659.  
#	Report the MGI ID, SwissProt ID(s), and GO ID(s) for all mouse
#	markers that have associated SwissProt sequences.

'''
 
import sys
import string
import os
import db
import reportlib

#
# Main
#

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init('gp2protein_SWP_TR', fileExt = '.mgi', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

# Retrieve Markers with GO Annotations

db.sql('select distinct m._Marker_key, a.accID ' + \
	'into #markers ' + \
	'from MRK_Marker m, ACC_Accession a ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and exists (select 1 from VOC_Annot v ' + \
	'where v._AnnotType_key = 1000 ' + \
	'and m._Marker_key = v._Object_key) ', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)

#
# select Markers that have SP or TrEMBL ids
#

results = db.sql('select m._Marker_key, a.accID, a._LogicalDB_key ' + \
	'from #markers m, ACC_Accession a ' + \
	'where m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key in (13, 41) ', 'auto')
spIDs = {}
for r in results:
    key = r['_Marker_key']

    if r['_LogicalDB_key'] == 13:
        value = 'SWP:' + r['accID']
    else:
        value = 'TR:' + r['accID']

    if not spIDs.has_key(key):
	spIDs[key] = []
    spIDs[key].append(value)

#
# select Markers that have protein id in their GO annotation inferred from field
#

results = db.sql('select distinct m._Marker_key, e.inferredFrom ' + \
	'from #markers m, VOC_Annot v, VOC_Evidence e ' + \
	'where v._AnnotType_key = 1000 ' + \
	'and m._Marker_key = v._Object_key ' + \
	'and v._Annot_key = e._Annot_key ' + \
	'and e.inferredFrom like "protein_id:%"', 'auto')
for r in results:
    key = r['_Marker_key']
    ids = string.split(r['inferredFrom'], 'protein_id:')
    for i in ids:
	if len(i) > 0:
	    value = 'Entrez:' + i
            if not spIDs.has_key(key):
	        spIDs[key] = []
	    if value not in spIDs[key]:
                spIDs[key].append(value)

results = db.sql('select distinct _Marker_key, accID from #markers order by accID', 'auto')

# number of unique MGI gene
fp.write('#   Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# total number of rows
fp.write('#   Total number of rows:  %s\n\n' % (len(results)))

for r in results:
    if spIDs.has_key(r['_Marker_key']):
        fp.write(r['accID'] + reportlib.TAB + \
	         string.join(spIDs[r['_Marker_key']], ';') + CRT)

reportlib.finish_nonps(fp)

