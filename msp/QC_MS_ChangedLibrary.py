#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Changed Libraries
#       from QC_MS_ChangedLibrary
#
# Usage:
#       QC_MS_ChangedLibrary.py OutputDir JobKey
#
# Notes:
#
# History:
#
# lec   05/10/2004
#       - created
#
'''
 
import os
import sys 
import db
import string
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

outputDir = os.environ['OUTPUTDIR']
jobStreamKey = os.environ['JOBSTREAM']
mgdDB = os.environ['MGDDBNAME']

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Changed Library (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir)

fp.write("  A row in this report represents a Sequence whose Library value has changed since it was last processed in MGI.\n" + 2*CRT)

fp.write(string.ljust('Sequence Acc ID', 30))
fp.write(string.ljust('Old Source key', 25))
fp.write(string.ljust('Old Raw Name', 50))
fp.write(string.ljust('Old Resolved Name', 50))
fp.write(string.ljust('New Source key', 25))
fp.write(string.ljust('New Raw Name', 50))
fp.write(string.ljust('New Resolved Name', 50))
fp.write(string.ljust('Found Method', 25))
fp.write(CRT)
fp.write(string.ljust('---------------', 30))
fp.write(string.ljust('--------------', 25))
fp.write(string.ljust('------------', 50))
fp.write(string.ljust('----------------', 50))
fp.write(string.ljust('--------------', 25))
fp.write(string.ljust('------------', 50))
fp.write(string.ljust('----------------', 50))
fp.write(string.ljust('------------', 25))
fp.write(CRT)

#
# select all records for given job stream which do not exists for another job stream
#

results = db.sql('select qc1.oldSource_key, qc1.oldRawName, qc1.oldResolvedName, ' + \
	   'qc1.newSource_key, qc1.newRawName, qc1.newResolvedName, qc1.foundMethod, ' + \
	   'a.accID ' + \
	   'from QC_MS_ChangedLibrary qc1, %s..ACC_Accession a ' % (mgdDB) + \
           'where qc1._JobStream_key = %s ' % (jobStreamKey) + \
	   'and qc1._Sequence_key = a._Object_key ' + \
	   'and a._MGIType_key = 19 ' + \
	   'and a.preferred = 1 ' + \
	   'and not exists (select 1 from QC_MS_ChangedLibrary qc2 ' + \
	   'where qc1._Sequence_key = qc2._Sequence_key ' + \
	   'and qc1._JobStream_key != qc2._JobStream_key) ' + \
	   ' order by qc1._Sequence_key', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['accID'], 30) + \
	     string.ljust(mgi_utils.prvalue(r['oldSource_key']), 25) + \
	     string.ljust(r['oldRawName'], 50) + \
	     string.ljust(r['oldResolvedName'], 50) + \
	     string.ljust(mgi_utils.prvalue(r['newSource_key']), 25) + \
	     string.ljust(mgi_utils.prvalue(r['newRawName']), 50) + \
	     string.ljust(mgi_utils.prvalue(r['newResolvedName']), 50) + \
	     string.ljust(mgi_utils.prvalue(r['foundMethod']), 25) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

