
'''
#
# TR 8618
#
# Report:
#
# List anatomical structures used in assays that have been annotated as having
# no expression, but the children used in the same assay have been annotated
# as having expression.
#
# Columns to display:
#    1) J-Number of the assay
#    2) MGI ID of the assay
#    3) Stage of the structures in question
#    4) Parent structure (with absent annotation)
#    5) Child structure
#    6) cell type
# 
# Originally requested as a custom SQL (TR 8073).
#
# Usage:
#       GXD_ChildExpNotParent.py
#
# History:
#
# sc    12/13/2021
#       - YAKS project - add cell type term
#
# lec	01/21/2016
#	- TR12223/gxd anatomy II
#
# lec   03/11/2014
#       - TR11597/sort by mgiID desc
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# dbm	11/28/2007
#	- new
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

fp = reportlib.init(sys.argv[0], 'Assays in which a parent structure is annotated as having no expression while its children have expression.', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Excluded J-Numbers: J:80501,J:80502,J:91257,J:93300,J:101679,J:122989,J:153498,J:162220,J:171409')
fp.write(2*CRT)
fp.write(str.ljust('J-Number', 12))
fp.write(SPACE)
fp.write(str.ljust('MGI ID', 12))
fp.write(SPACE)
fp.write(str.ljust('Stage', 5))
fp.write(SPACE)
fp.write(str.ljust('Parent Structure', 50))
fp.write(SPACE)
fp.write(str.ljust('Child Structure', 50))
fp.write(SPACE)
fp.write(str.ljust('Cell Type', 35))
fp.write(CRT)
fp.write(12*'-')
fp.write(SPACE)
fp.write(12*'-')
fp.write(SPACE)
fp.write(5*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(SPACE)
fp.write(35*'-')
fp.write(CRT)

#
# Identify all cases where the parent structure has no expression (strength = 1), 
# but has a child that does have expression (strength > 1).
#

db.sql('''
select distinct 
        a._Assay_key, 
        sp._Specimen_key as sp1Key, 
        sp2._Specimen_key as sp2Key, 
        r._Result_key as r1Key, 
        r2._Result_key as r2Key
        into temporary table work1
        from GXD_Assay a,
             GXD_Specimen sp,
             GXD_Specimen sp2,
             GXD_InSituResult r,
             GXD_InSituResult r2,
             VOC_Term rt,
             VOC_Term r2t
        where a._AssayType_key in (1,2,3,4,5,6,8,9)
              and a._Refs_key not in (81462,81463,92242,94290,102744,124081,154591,154591,163316,172505)
              and a._Assay_key = sp._Assay_key
              and sp._Specimen_key = r._Specimen_key
              and r._Strength_key = rt._term_key and rt.term = 'Absent'
              and sp._Assay_key = sp2._Assay_key
              and sp._Genotype_key = sp2._Genotype_key
              and sp.age = sp2.age
              and sp2._Specimen_key = r2._Specimen_key
              and r2._Strength_key = r2t._term_key and r2t.term not in ('Absent', 'Not Applicable', 'Not Specified')
              and sp._Genotype_key = sp2._Genotype_key 
              and sp.age = sp2.age 
        ''', None)

db.sql('create index work1_idx1 on work1(_Assay_key)', None)
db.sql('create index work1_idx2 on work1(sp1Key)', None)
db.sql('create index work1_idx3 on work1(sp2Key)', None)
db.sql('create index work1_idx4 on work1(r1Key)', None)
db.sql('create index work1_idx5 on work1(r2Key)', None)

db.sql('''
        select distinct
               a._Assay_key,
               s._EMAPA_Term_key as parentKey, 
               s._Stage_key,
               s2._EMAPA_Term_key as childKey,
               a.r2Key
        into temporary table work2
        from work1 a,
             GXD_ISResultStructure s, GXD_ISResultStructure s2, 
             DAG_Closure c, VOC_Term_EMAPS emaps_p, VOC_Term_EMAPS emaps_c
        where a.r1Key = s._Result_key
              and a.r2Key = s2._Result_key
              and s._Stage_key = s2._Stage_key
              and s._EMAPA_Term_key = emaps_p._EMAPA_Term_key
              and emaps_p._Term_key = c._AncestorObject_key
              and c._MGIType_key = 13
              and c._DescendentObject_key = emaps_c._Term_key
              and emaps_c._EMAPA_Term_key = s2._EMAPA_Term_key
        ''', None)

db.sql('create index work2_idx1 on work2(_Assay_key)', None)
db.sql('create index work2_idx2 on work2(parentKey)', None)
db.sql('create index work2_idx3 on work2(childKey)', None)
db.sql('create index work2_idx4 on work2(_Stage_key)', None)

# bring in the cell type term key associated with the parent structure, which can be null
db.sql(''' select w.*, e._celltype_term_key
        into temporary table work3
        from work2 w, gxd_expression e
        where w._assay_key = e._assay_key
        and w.parentKey = e._EMAPA_Term_key
        and w._stage_key = e._stage_key
        ''', None)

db.sql('create index work3_idx1 on work3(_celltype_term_key)', None)

# get the term if the celltype term key is not null
db.sql(''' select w.*, t.term as celltypeTerm
        into temporary table work4
        from work3 w
        left outer join voc_term t on (w._celltype_term_key = t._term_key)''', None)

db.sql('create index work4_idx1 on work4(_Assay_key)', None)
db.sql('create index work4_idx2 on work4(parentKey)', None)
db.sql('create index work4_idx3 on work4(childKey)', None)
db.sql('create index work4_idx4 on work4(_Stage_key)', None)

results = db.sql('''
        select distinct 
               a.accID as mgiID, 
               j.accID as jnumID, 
               t.stage, 
               substring(d.term,1,50) as pterm, 
               substring(d2.term,1,50) as cterm,
               substring(w.celltypeTerm,1,50) as celltype
        from work4 w, GXD_Assay ga, ACC_Accession a, ACC_Accession j,
             VOC_Term d, VOC_Term d2, GXD_TheilerStage t
        where w._Assay_key = ga._Assay_key
              and ga._Assay_key = a._Object_key 
              and a._MGIType_key = 8 
              and ga._Refs_key = j._Object_key 
              and j._MGIType_key = 1 
              and j.prefixPart = 'J:' 
              and w.parentKey = d._Term_key 
              and w.childKey = d2._Term_key
              and w._Stage_key = t._Stage_key
              order by mgiID desc, t.stage, pterm, cterm
        ''', 'auto')
fp.write('\n(%d rows affected)\n\n' % (len(results)))

for r in results:
        celltype = r['celltype']
        if celltype == None:
            celltype = ''
        fp.write(str.ljust(r['jnumID'], 12))
        fp.write(SPACE)
        fp.write(str.ljust(r['mgiID'], 12))
        fp.write(SPACE)
        fp.write(str.ljust(str(r['stage']), 5))
        fp.write(SPACE)
        fp.write(str.ljust(r['pterm'], 50))
        fp.write(SPACE)
        fp.write(str.ljust(r['cterm'], 50))
        fp.write(SPACE)
        fp.write(str.ljust(celltype, 35))
        fp.write(CRT)

reportlib.finish_nonps(fp)
