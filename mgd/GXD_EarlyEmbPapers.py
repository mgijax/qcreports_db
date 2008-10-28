#!/usr/local/bin/python

'''
#
# TR 9313 Early embryonic expression papers
#
# Report:
#
# Usage:
#       GXD_EarlyEmbPapers.py
#
# History:
#
# lec	10/28/2008
#	- TR9349, only select high and medium priority
#
# lec	10/21/2008
#	- TR 9313
#
'''

import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], 'Early Embryonic Expression Papers', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('papers not coded whose index records only contain E0.5-7.5 and A data' + CRT)
fp.write(2*CRT)

fp.write(string.ljust('J#', 10))
fp.write(SPACE)
fp.write(string.ljust('index records', 15))
fp.write(SPACE)
fp.write(string.ljust('new genes', 15))
fp.write(SPACE)
fp.write(string.ljust('priority score', 15))
fp.write(CRT)

fp.write(string.ljust('--------', 10))
fp.write(SPACE)
fp.write(string.ljust('-------------', 15))
fp.write(SPACE)
fp.write(string.ljust('---------', 15))
fp.write(SPACE)
fp.write(string.ljust('--------------', 15))
fp.write(CRT)

#
# E0.5-7.5, A
#

db.sql('''
    select distinct _Refs_key, _Priority_key, priority = p.term
    into #refs1
    from GXD_Index gi, 
         GXD_Index_Stages gis, 
         VOC_Term vts,
	 VOC_Term p
    where gi._Refs_key not in (select _Refs_key from GXD_Assay)
    and gi._Index_key = gis._Index_key
    and gis._StageID_key = vts._Term_key
    and vts._Vocab_key = 13
    and vts.term in ('0.5','1','1.5','2','2.5','3','3.5','4','5.5','6','6.5','7','7.5','A')
    and gi._Priority_key in (74715, 74714)
    and gi._Priority_key = p._Term_key
    ''', None)

db.sql('create index idx1 on #refs1(_Refs_key)', None)

#
# delete records that have index data that is other than E0.5-7.5, A
# because we are only interested in data that has ONLY E0.5-7.5, A.
#

db.sql('''
    delete #refs1
    from #refs1 r
    where exists (select 1
     from GXD_Index gi, 
          GXD_Index_Stages gis, 
          VOC_Term vts
     where r._Refs_key = gi._Refs_key
     and gi._Index_key = gis._Index_key
     and gis._StageID_key = vts._Term_key
     and vts._Vocab_key = 13
     and vts.term in ('8','8.5','9','9.5','10','10.5','11','11.5','12','12.5','13','13.5','14','14.5','15','15.5','16','16.5','17','17.5','18','18.5','19','19.5','20','E'))
    ''', None)

#
# select number of indexes
#

db.sql('''
    select r._Refs_key, r._Priority_key, r.priority, numIndexes = count(_Index_key)
    into #refs2
    from #refs1 r, GXD_Index gi 
    where r._Refs_key = gi._Refs_key
    group by r._Refs_key
    ''', None)

db.sql('create index idx1 on #refs2(_Refs_key)', None)

#
# select number of new genes (genes in index but not in expression cache)
#

# those genes that are not in the cache
db.sql('''
    select r._Refs_key, r._Priority_key, r.priority, r.numIndexes, numGenes = count(_Index_key)
    into #final
    from #refs2 r, GXD_Index gi 
    where r._Refs_key = gi._Refs_key
    and not exists (select 1 from GXD_Expression e where gi._Marker_key = e._Marker_key)
    group by r._Refs_key
    ''', None)

# those genes that are in the cache
db.sql('''
    insert into #final
    select r._Refs_key, r._Priority_key, r.priority, r.numIndexes, numGenes = 0
    from #refs2 r, GXD_Index gi 
    where r._Refs_key = gi._Refs_key
    and not exists (select 1 from #final f where r._Refs_key = f._Refs_key)
    and exists (select 1 from GXD_Expression e where gi._Marker_key = e._Marker_key)
    group by r._Refs_key
    ''', None)

db.sql('create index idx1 on #final(_Refs_key)', None)

#
# final report
#

results = db.sql('''
   select b.jnumID, f.*
   from #final f, BIB_Citation_Cache b
   where f._Refs_key = b._Refs_key
   order by  f._Priority_key, f.numGenes desc, f.numIndexes desc
   ''', 'auto')

for r in results:
	fp.write(string.ljust(r['jnumID'], 10))
	fp.write(SPACE)
	fp.write(string.ljust(str(r['numIndexes']), 15))
	fp.write(SPACE)
	fp.write(string.ljust(str(r['numGenes']), 15))
	fp.write(SPACE)
	fp.write(string.ljust(r['priority'], 15) + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
db.useOneConnection(0)

