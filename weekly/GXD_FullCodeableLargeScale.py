
'''
#
# Report:
#
# Full-coded data only from large scale screens
#
#       J# for large scale screens: see below
#
#       List all markers with only full-coded is from large scale J# 
#
#       MGI ID of marker gene symbol
#
#       For each marker list the number of papers: indexed, fullcoded
#
# Add a new column - Difference.  It is the Index records column minus the full-coded column.
# Suppress all rows where Difference = 0.
# New primary sort: Difference, in Descending order (ie biggest # at top); secondary sort:  Symbol.
# 
# History:
#
# lec	09/05/2023
#	- wts2-1268/2 new GXD QC reports for fullcoding priority
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Full-coded data only from large scale screens', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('''
        J# for large scale screens:
        J:101679 J:122989 J:140465 J:141291 J:143778 J:153498 J:157819 J:162220 J:171409 J:313619 
        J:215487 J:226028 J:228563 J:279207 J:46439 J:80501 J:80502 J:85124 J:91257 J:93300

        index records by marker = # of all references from gxd_index
        full-coded by marker = # of large scale references from gxd_expression_cache
        difference = index records minus full-coded

''')

fp.write(str.ljust('acc id', 25))
fp.write(SPACE)
fp.write(str.ljust('symbol', 35))
fp.write(SPACE)
fp.write(str.ljust('index records', 20))
fp.write(SPACE)
fp.write(str.ljust('full-coded', 20))
fp.write(SPACE)
fp.write(str.ljust('difference', 20))
fp.write(SPACE)
fp.write(CRT*2)

#
# count: all genes in the GXD index by marker
#
db.sql('''
select g._Marker_key, count(*) as idx_count 
into temp table idxcount
from GXD_Index g
group by g._Marker_key
''', 'auto')
db.sql('create index index_idx1 on idxcount(_marker_key)', None)

#
# count:  all full-coded genes in large scale references
# where large scale references are the *only* references for the marker
# group by marker, reference
#
db.sql('''
select a._marker_key, a._refs_key, count(*) as full_count
into temp table refcount
from GXD_Assay a, BIB_Citation_Cache c
where c.jnumid in (
'J:101679', 'J:122989', 'J:140465', 'J:141291', 'J:143778', 'J:153498', 'J:157819', 'J:162220', 'J:171409', 'J:313619',
'J:215487', 'J:226028', 'J:228563', 'J:279207', 'J:46439', 'J:80501', 'J:80502', 'J:85124', 'J:91257', 'J:93300'
)
and c._refs_key = a._refs_key
and exists (select 1 from GXD_Expression g where a._Assay_key = g._Assay_key)
and a._assaytype_key not in (10,11)
and not exists (select 1 from GXD_Assay aa, BIB_Citation_Cache cc
        where a._marker_key = aa._marker_key
        and cc.jnumid not in (
        'J:101679', 'J:122989', 'J:140465', 'J:141291', 'J:143778', 'J:153498', 'J:157819', 'J:162220', 'J:171409', 'J:313619',
        'J:215487', 'J:226028', 'J:228563', 'J:279207', 'J:46439', 'J:80501', 'J:80502', 'J:85124', 'J:91257', 'J:93300'
        )
        and cc._refs_key = aa._refs_key
        and aa._assaytype_key not in (10,11)
        )
group by a._marker_key, a._refs_key
''', None)
db.sql('create index full_idx1 on refcount(_marker_key)', None)

#
# group by marker only
#
db.sql('''
select g._marker_key, m.symbol, a.accID, count(g.full_count) as full_count
into temporary table allgenes
from refcount g, MRK_Marker m, ACC_Accession a
where g._marker_key = m._marker_key
and g._marker_key = a._object_key
and a._mgitype_key = 2
and a._logicaldb_key = 1
and a.preferred = 1
group by g._marker_key, m.symbol, a.accID
''', None)
db.sql('create index allgenes_idx1 on allgenes(_marker_key)', None)

#
# to print...
#
results = db.sql('''
select a.*, i.*, i.idx_count - a.full_count as difference
from allgenes a, idxcount i
where a._marker_key = i._marker_key
and i.idx_count - a.full_count > 0
order by difference desc, symbol
''', 'auto')

for r in results:

    key = r['_Marker_key']

    fp.write(str.ljust(r['accID'], 25))
    fp.write(SPACE)
    fp.write(str.ljust(r['symbol'], 35))
    fp.write(SPACE)
    fp.write(str.ljust(str(r['idx_count']), 20))
    fp.write(SPACE)
    fp.write(str.ljust(str(r['full_count']), 20) + SPACE)
    fp.write(str.ljust(str(r['difference']), 20) + CRT)
        
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

