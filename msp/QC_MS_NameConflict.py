#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Clone Library Conficts
#       from QC_MS_NameConflict.
#
# Usage:
#       QC_MS_NameConflict.py OutputDir JobKey MGDDBinstance
#
# Notes:
#
# History:
#
# lec   03/24/2004
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
mgdDB = sys.argv[3]	# not used

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Library Conflicts (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir)

fp.write("  A row in this report represents a discrepency between the Clone Libraries\n" + \
"  of any of a Sequence's associated Clones.  If a Sequence's Library cannot be\n" + \
"  resolved or is Anonymous, and any of its associated Clones are defined by more\n" + \
"  than one Library, the Sequence and those Libraries will appear on this report." + 2*CRT)

fp.write(string.ljust('Sequence ID', 16))
fp.write(string.ljust('Library Name 1', 45))
fp.write(string.ljust('Library Name 2', 45))
fp.write(CRT)
fp.write(string.ljust('-----------', 16))
fp.write(string.ljust('--------------', 45))
fp.write(string.ljust('--------------', 45))
fp.write(CRT)

results = db.sql('select qc.accID, qc.libName1, libName2 ' + \
	    'from QC_MS_NameConflict qc ' + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'order by qc.accID', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['accID'], 16) + \
             string.ljust(r['libName1'], 45) + \
             string.ljust(r['libName2'], 45) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

