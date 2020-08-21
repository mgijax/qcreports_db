
'''
#
# TR 12250 LitTriage Project
#
# Report:
#
# Report references that are marked as "MGI discard" and have data associated 
# with them 
#
# order by descending J#
#
# Usage:
#       MRK_BIB_Discard
#
# Notes:
#
# History:
#
# sc   10/09/2017
#       - TR12250 created
#
'''

import sys
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'References that are marked as "MGI discard" and have data associated with them', os.environ['QCOUTPUTDIR'])

results = db.sql('''select distinct a.accid as jNum, a.numericPart
    from BIB_Refs b, MRK_Reference m, ACC_Accession a
    where b.isDiscard = 1
    and b._Refs_key = m._Refs_key
    and m._Refs_key = a._Object_key
    and a._MGIType_key = 1
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and prefixPart = 'J:' ''', 'auto')
for r in results:
    fp.write('%s%s' % (r['jNum'], CRT))

fp.write('Total: %s' % len(results))
reportlib.finish_nonps(fp)      # non-postscript file
