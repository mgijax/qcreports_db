#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Sequence Raw Source Attribute Discrepencies
#       from QC_SEQ_RawSourceConflict
#
# Usage:
#       QC_MS_RawSourceConflict.py OutputDir JobKey MGDDBinstance
#
# Notes:
#
# History:
#
# lec   03/30/2004
#       - created
#
'''
 
import sys 
import db
import string
import reportlib
import os

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

outputDir = sys.argv[1]
jobStreamKey = sys.argv[2]

mgdDB = os.environ['MGD_DBNAME']
radarDB = os.environ['RADAR_DBNAME']
server = os.environ['RADAR_DBSERVER']
db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Sequence Loader - Sequence Raw Source Attribute Discrepencies (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents a Sequence Raw Source Attribute (Library or \n" + \
"  Organism only) where its new raw value differs from its old raw value." + 2*CRT)

fp.write(string.ljust('Sequence ID', 25))
fp.write(string.ljust('Attribute', 25))
fp.write(string.ljust('New Raw Value', 35))
fp.write(string.ljust('Old Raw Value', 35))
fp.write(string.ljust('Old Resolved Value', 35))
fp.write(CRT)
fp.write(string.ljust('-----------', 25))
fp.write(string.ljust('---------', 25))
fp.write(string.ljust('-------------', 35))
fp.write(string.ljust('-------------', 35))
fp.write(string.ljust('------------------', 35))
fp.write(CRT)

results = db.sql('select seqID = a.accID, qc.attrName, ' + \
	    'newRaw = qc.incomingValue, oldRaw = sr.rawLibrary, oldResolved = ps.name ' + \
	    'from QC_SEQ_RawSourceConflict qc, ' + \
	    '%s..ACC_Accession a, %s..SEQ_Sequence s, %s..SEQ_Sequence_Raw sr, ' % (mgdDB, mgdDB, mgdDB) + \
	    '%s..SEQ_Source_Assoc sa, %s..PRB_Source ps ' % (mgdDB, mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc._Sequence_key = a._Object_key ' + \
	    'and attrName = "library" ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and a.preferred = 1 ' + \
	    'and qc._Sequence_key = s._Sequence_key ' + \
	    'and s._Sequence_key = sa._Sequence_key ' + \
	    'and s._Sequence_key = sr._Sequence_key ' + \
	    'and sa._Source_key = ps._Source_key ' + \
	    'union ' + \
            'select seqID = a.accID, qc.attrName, ' + \
	    'newRaw = qc.incomingValue, oldRaw = sr.rawOrganism, oldResolved = o.commonName ' + \
	    'from QC_SEQ_RawSourceConflict qc, %s..ACC_Accession a, %s..SEQ_Sequence s, ' % (mgdDB, mgdDB) + \
	    '%s..SEQ_Sequence_Raw sr, ' % mgdDB + \
	    '%s..SEQ_Source_Assoc sa, %s..PRB_Source ps, %s..MGI_Organism o ' % (mgdDB, mgdDB, mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc._Sequence_key = a._Object_key ' + \
	    'and attrName = "organism" ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and a.preferred = 1 ' + \
	    'and qc._Sequence_key = s._Sequence_key ' + \
	    'and s._Sequence_key = sa._Sequence_key ' + \
	    'and s._Sequence_key = sr._Sequence_key ' + \
	    'and sa._Source_key = ps._Source_key ' + \
	    'and ps._Organism_key = o._Organism_key ' + \
	    'order by seqID', 'auto')

rows = 0
for r in results:
    newRaw = r['newRaw']
    if newRaw == None:
	newRaw = "NULL"
    oldRaw = r['oldRaw']
    if oldRaw == None:
	oldRaw = "NULL"
    oldResolved = r['oldResolved']
    if oldResolved == None:
        oldResolved = "NULL"
    fp.write(string.ljust(r['seqID'], 25) + \
             string.ljust(r['attrName'], 25) + \
             string.ljust(newRaw, 35) + \
             string.ljust(oldRaw, 35) + \
             string.ljust(oldResolved, 35) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.finish_nonps(fp)

