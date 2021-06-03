
'''
#
# WTS2-619/Lit Triage
#
# Report:
#
#	The reference must be:
#	group = AP, tag = AP:Indexing_needed
#
#	output:
#       1. MGI Id of reference
#       2. Publication Year
#       3. indexed gene/marker symboli
#       4. indexed gene/merker ID
#
# Usage:
#       WF_AP_IndexingNeeded.py
#
# Notes:
#
# History:
#
# 05/19/2021
#	- WTS2-619/Lit Triage
#
'''
 
import sys 
import os 
import re
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

counter = 0
refKeyList = []

#
# Main
#

fp = reportlib.init(sys.argv[0], 'AP:Indexing_needed papers with genes', os.environ['QCOUTPUTDIR'])

fp.write('''
        The reference must be:
             group = AP, tag = AP:Indexing_needed\n
''')
db.sql('''select ra._refs_key, ra._object_key as _marker_key, b.year, 
        a.accid as refID
    into temporary table markerRefs
    from mgi_reference_assoc ra, BIB_Refs b, ACC_Accession a
    where ra._refassoctype_key = 1018 -- general, strain-specific marker is 1028
    and ra._refs_key = b._refs_key
    and ra._refs_key = a._object_key
    and a._mgitype_key = 1
    and a._logicaldb_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:' ''', None)
db.sql('''create index idx1 on markerRefs(_refs_key)''', None)

db.sql('''create index idx2 on markerRefs(_marker_key)''', None)

results = db.sql('''select distinct m.symbol, a.accid as markerID, r.* 
    from BIB_Workflow_Tag t, markerRefs r, mrk_marker m, acc_accession a
    where t._tag_key = 35710201 --AP:Indexing_needed
    and t._Refs_key = r._Refs_key
    and r._marker_key = m._marker_key
    and m._marker_key = a._object_key
    and a._mgitype_key = 2
    and a._logicaldb_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    order by r._refs_key, m.symbol''', 'auto')

#
# print report
#
for r in results:
    if r['_refs_key'] not in refKeyList:
        refKeyList.append(r['_refs_key'])
    fp.write('%s%s%s%s%s%s%s%s' % ( r['refID'], TAB, r['year'], TAB, r['symbol'], TAB, r['markerID'], CRT))
    counter += 1

fp.write('%s%s rows affected%s' % (CRT, counter, CRT))
fp.write('%s%s distinct references%s' % (CRT, len(refKeyList), CRT))
reportlib.finish_nonps(fp)
