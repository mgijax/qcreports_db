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
# lec	09/23/2009
#	- TR9806; add conditional column
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
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'Early Embryonic Expression Papers', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('papers not coded whose index records only contain E0.5-7.5 and A data' + CRT)
fp.write(2*CRT)

fp.write(str.ljust('J#', 10))
fp.write(SPACE)
fp.write(str.ljust('index records', 15))
fp.write(SPACE)
fp.write(str.ljust('new genes', 15))
fp.write(SPACE)
fp.write(str.ljust('priority score', 15))
fp.write(SPACE)
fp.write(str.ljust('conditional', 15))
fp.write(CRT)

fp.write(str.ljust('--------', 10))
fp.write(SPACE)
fp.write(str.ljust('-------------', 15))
fp.write(SPACE)
fp.write(str.ljust('---------', 15))
fp.write(SPACE)
fp.write(str.ljust('--------------', 15))
fp.write(SPACE)
fp.write(str.ljust('--------------', 15))
fp.write(CRT)

#
# E0.5-7.5, A
#

db.sql('''
    select distinct _Refs_key, _Priority_key, 
           p.term as priority, c.term as conditional
    into temp table refs1
    from GXD_Index gi, 
         GXD_Index_Stages gis, 
         VOC_Term vts,
         VOC_Term p,
         VOC_Term c
    where gi._Refs_key not in (select _Refs_key from GXD_Assay)
    and gi._Index_key = gis._Index_key
    and gis._StageID_key = vts._Term_key
    and vts._Vocab_key = 13
    and vts.term in ('0.5','1','1.5','2','2.5','3','3.5','4','5.5','6','6.5','7','7.5','A')
    and gi._Priority_key in (74715, 74714)
    and gi._Priority_key = p._Term_key
    and gi._ConditionalMutants_key = c._Term_key
    ''', None)

db.sql('create index refs1_idx1 on refs1(_Refs_key)', None)

#
# delete records that have index data that is other than E0.5-7.5, A
# because we are only interested in data that has ONLY E0.5-7.5, A.
#

db.sql('''
    delete
    from refs1
    where exists (select 1
     from GXD_Index gi, 
          GXD_Index_Stages gis, 
          VOC_Term vts
     where refs1._Refs_key = gi._Refs_key
     and gi._Index_key = gis._Index_key
     and gis._StageID_key = vts._Term_key
     and vts._Vocab_key = 13
     and vts.term in ('8','8.5','9','9.5','10','10.5','11','11.5','12','12.5','13','13.5','14','14.5','15','15.5','16','16.5','17','17.5','18','18.5','19','19.5','20','E'))
    ''', None)

#
# select number of indexes
#

db.sql('''
    select r._Refs_key, count(_Index_key) as numindexes
    into refs2
    from refs1 r, GXD_Index gi 
    where r._Refs_key = gi._Refs_key
    group by r._Refs_key
    ''', None)

db.sql('create index refs2_idx1 on refs2(_Refs_key)', None)

#
# select number of new genes (genes in index but not in expression cache)
#

# those genes that are not in the cache
db.sql('''
    select r._Refs_key, count(_Index_key) as numgenes
    into temp table final
    from refs2 r, GXD_Index gi 
    where r._Refs_key = gi._Refs_key
    and not exists (select 1 from GXD_Expression e where gi._Marker_key = e._Marker_key)
    group by r._Refs_key
    ''', None)

# those genes that are in the cache
db.sql('''
    insert into final
    select r._Refs_key, 0
    from refs2 r, GXD_Index gi 
    where r._Refs_key = gi._Refs_key
    and not exists (select 1 from final f where r._Refs_key = f._Refs_key)
    and exists (select 1 from GXD_Expression e where gi._Marker_key = e._Marker_key)
    group by r._Refs_key
    ''', None)

db.sql('create index final_idx1 on final(_Refs_key)', None)

#
# final report
#

results = db.sql('''
   select b.jnumID, f.*, r1._Priority_key, r1.priority, r1.conditional, r2.numindexes
   from final f, BIB_Citation_Cache b, refs1 r1, refs2 r2
   where f._Refs_key = b._Refs_key
   and f._Refs_key = r1._Refs_key
   and f._Refs_key = r2._Refs_key
   order by  r1._Priority_key, f.numgenes desc, r2.numindexes desc
   ''', 'auto')

for r in results:
        fp.write(str.ljust(r['jnumID'], 10))
        fp.write(SPACE)
        fp.write(str.ljust(str(r['numindexes']), 15))
        fp.write(SPACE)
        fp.write(str.ljust(str(r['numgenes']), 15))
        fp.write(SPACE)
        fp.write(str.ljust(r['priority'], 15))
        fp.write(SPACE)
        fp.write(str.ljust(r['conditional'], 15) + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
