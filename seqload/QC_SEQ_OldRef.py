#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of defunct MGI Sequence/Reference Associations
#       from QC_SEQ_OldRef
#
# Usage:
#       QC_MS_OldRef.py OutputDir JobKey MGDDBinstance
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

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

outputDir = sys.argv[1]
jobStreamKey = sys.argv[2]
mgdDB = sys.argv[3]

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Sequence Loader - Defunct MGI Sequence/Reference Associations (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir)

fp.write("  A row in this report represents a Sequence/Reference association that\n" + \
"  is no longer in the Sequence provider record." + 2*CRT)

fp.write(string.ljust('Sequence ID', 25))
fp.write(string.ljust('J:', 15))
fp.write(string.ljust('Citation', 25))
fp.write(CRT)
fp.write(string.ljust('-----------', 25))
fp.write(string.ljust('-----------', 15))
fp.write(string.ljust('-----------', 25))
fp.write(CRT)

results = db.sql('select seqID = a.accID, b.jnumID, b.short_citation ' + \
	    'from QC_SEQ_OldRef qc, %s..ACC_Accession a, %s..BIB_All_View b ' % (mgdDB, mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc._Sequence_key = a._Object_key ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and a.preferred = 1 ' + \
	    'and qc._Refs_key = b._Refs_key ' + \
	    'order by seqID', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['seqID'], 25) + \
             string.ljust(r['jnumID'], 15) + \
             string.ljust(r['short_citation'], 25) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

