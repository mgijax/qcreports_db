#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Source Attribute Discrepencies
#       from QC_MS_AttrEdit.
#
# Usage:
#       QC_MS_AttrEdit.py OutputDir JobKey MGDDBinstance
#
# Notes:
#
# History:
#
# lec   03/17/2004
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
		    'Molecular Source Processer - Source Attribute Discrepency (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir)

fp.write(string.ljust('Sequence ID', 25))
fp.write(string.ljust('Attribute Name', 55))
fp.write(string.ljust('MGI Value', 55))
fp.write(string.ljust('Incoming Value', 55))
fp.write(CRT)
fp.write(string.ljust('-----------', 25))
fp.write(string.ljust('--------------', 55))
fp.write(string.ljust('---------', 55))
fp.write(string.ljust('--------------', 55))
fp.write(CRT)

results = db.sql('select a.accID, qc.attrName, qc.incomingValue ' + \
	   'from QC_MS_AttrEdit qc, %s..SEQ_Source_Assoc sa, %s..SEQ_Sequence_Acc_View a ' % (mgdDB, mgdDB) + \
           'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	   'and qc.source_key = sa._Source_key ' + \
	   'and sa._Sequence_key = a._Object_key ' + \
	   ' order by a.accID', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['accID'], 25) + \
             string.ljust(r['attrName'], 55) + \
             string.ljust(r['attrValue'], 55) + \
             string.ljust(r['incomingValue'], 55) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

