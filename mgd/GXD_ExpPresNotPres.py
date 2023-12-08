
'''
#
# TR 8053/TR 7945
#
# Report:
#       Produce a report of assays for which the same structure has been
#       coded as having expression both present and absent.  Note the
#       following conditions:
#
#       .) Limit the comparison to structures within the same assay.
#       .) Limit the comparison to specimens with the same genotype.
#       .) Limit the comparison to speciment with the same sex.
#       .) Limit the comparison to specimens with the same age.
#       .) A structure is considered to be a combination of Theiler stage
#          and body part (e.g. TS11;embryo).
#       .) Absence of staining is when strength is "Absent".  Presence
#          of staining is anything other than "Absent".
#       .) Exclude assays with any of these references: J:46439,
#          J:50869, J:91257, J:93500, J:93300, J:99307, J:122989, J:171409
#
#       The report should have the following columns:
#
#       1) J Number for the assay
#       2) MGI ID of the assay
#       3) Structure in question
#
# Usage:
#       GXD_ExpPresNotPres.py
#
# History:
#
# sc    12/13/2021
#       - YAKS project - add cell type term
#
# lnh 11/20/2015
#       - TR12134 GXD QC report needs more ordering
#         sort by structure
#
# lec	03/11/2014
#	- TR11597/sort by mgiID desc
#
# lec	10/12/2011
#	- TR10877; exclude J:174767 [Surani load; TR10840]
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# lec	12/07/2006
#	- TR 8053; converted to QC report
#
# dbm    11/6/2006    created
#
'''

import sys
import os
import reportlib
import db

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

#
# Open the output file and write a header to it.
#
reportTitle = 'Assays in which the same anatomical structure is annotated as having expression both present and absent'

fp = reportlib.init(sys.argv[0], title = reportTitle, outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Excluded:\n')
fp.write('\tJ:46439, J:50869, J:91257, J:93500, J:93300, J:99307, J:174767, J:122989, J:171409\n')
fp.write('\treproductive system, 16-19\n\n')

fp.write('Specimens must have the same genotype and age\n\n')
fp.write('J Number   ')
fp.write('MGI ID        ')
fp.write('Stage:EMAPA                                         ')
fp.write('Cell Type' + CRT)
fp.write('---------  ')
fp.write('------------  ')
fp.write('--------------------------------------------------  ')
fp.write('--------------------------------------------------' + CRT)

# excluded references
db.sql('''
        select a._Object_key as _Refs_key
        into temporary table excludeRefs 
        from ACC_Accession a 
        where a._MGIType_key = 1 
        and a._LogicalDB_key = 1 
        and a.accID in 
                ('J:46439','J:50869','J:91257','J:93500','J:93300','J:99307', 'J:174767', 'J:122989', 'J:171409')
        ''', None)
db.sql('create index excludeRefs_idx1 on excludeRefs(_Refs_key)', None)

db.sql('''
    SELECT DISTINCT s._EMAPA_Term_key, s._Stage_key
    INTO TEMPORARY TABLE excludeStructs
    FROM VOC_Term t, DAG_Closure c, VOC_Term tt, VOC_Term_EMAPS s
    WHERE t._Vocab_key = 91
      AND t._Term_key = c._AncestorObject_key
      AND c._MGIType_key = 13
      AND c._DescendentObject_key = tt._Term_key
      AND tt._Term_key = s._Term_key
      AND t.term = 'reproductive system' AND s._Stage_key between 16 and 19
    UNION 
    SELECT DISTINCT s._EMAPA_Term_key, s._Stage_key
    FROM VOC_Term t, VOC_Term_EMAPS s
    WHERE t._Vocab_key = 91
      AND t._Term_key = s._Term_key
      AND t.term = 'reproductive system' AND s._Stage_key between 16 and 19
        ''', None)
db.sql('create index excludeStructs_idx1 on excludeStructs(_EMAPA_Term_key)', None)
db.sql('create index excludeStructs_idx2 on excludeStructs(_Stage_key)', None)

#
# assays with expression
#
db.sql('''
        select distinct e._Assay_key, e._Refs_key, e._EMAPA_Term_key, e._Stage_key, e._Genotype_key, e.age, e._celltype_Term_key
        into temporary table expressed 
        from GXD_Expression e 
        where e.isForGXD = 1 
        and e.expressed = 1 
        and not exists (select 1 from excludeStructs r 
                where e._EMAPA_Term_key = r._EMAPA_Term_key and e._Stage_key = r._Stage_key) 
        and not exists (select 1 from excludeRefs r where e._Refs_key = r._Refs_key)
        ''', None)
db.sql('create index expressed_idx1 on expressed(_Assay_key)', None)
db.sql('create index expressed_idx2 on expressed(_EMAPA_Term_key)', None)
db.sql('create index expressed_idx3 on expressed(_Stage_key)', None)
db.sql('create index expressed_idx4 on expressed(_Genotype_key)', None)
db.sql('create index expressed_idx5 on expressed(age)', None)
db.sql('create index expressed_idx6 on expressed(_celltype_Term_key)', None)
#
# compare expressed/not expressed by assay, structure, stage, genotype, age, and cell type
#
db.sql('''
        select distinct e.*
        into temporary table results1 
        from expressed e, GXD_Expression n 
        where e._Assay_key = n._Assay_key 
        and n.isForGXD = 1 
        and e._EMAPA_Term_key = n._EMAPA_Term_key 
        and e._Stage_key = n._Stage_key 
        and e._Genotype_key = n._Genotype_key 
        and e.age = n.age 
        and e._celltype_Term_key =  n._celltype_Term_key
        and n.expressed = 0 
        union
        select distinct e.*
        from expressed e, GXD_Expression n
        where e._Assay_key = n._Assay_key
        and n.isForGXD = 1
        and e._EMAPA_Term_key = n._EMAPA_Term_key
        and e._Stage_key = n._Stage_key
        and e._Genotype_key = n._Genotype_key
        and e.age = n.age
        and e._celltype_Term_key is null
        and n._celltype_Term_key is null
        and n.expressed = 0
        ''', None)

db.sql('create index results1_idx1 on results1(_celltype_term_key)', None)

db.sql('''
        select r.*, t.term as celltypeTerm
        into temporary table results2
        from results1  r
        left outer join VOC_Term t on (r._celltype_term_key = t._term_key)''', None)

db.sql('create index results2_idx1 on results2(_Assay_key)', None)
db.sql('create index results2_idx2 on results2(_EMAPA_Term_key)', None)
db.sql('create index results2_idx3 on results2(_Stage_key)', None)
db.sql('create index results2_idx4 on results2(_Refs_key)', None)

#
# final results
#
results = db.sql('''
        select ac1.accID as jnumID, 
               ac2.accID as mgiID, 
               t.stage::text || ':' || s.term as term,
               r.celltypeTerm
         from results2 r, VOC_Term s, GXD_TheilerStage t, 
              ACC_Accession ac1, ACC_Accession ac2 
         where r._EMAPA_Term_key = s._Term_key 
         and r._Stage_key = t._Stage_key 
         and r._Refs_key = ac1._Object_key 
         and ac1._LogicalDB_key = 1 
         and ac1._MGIType_key = 1 
         and ac1.prefixPart = 'J:' 
         and r._Assay_key = ac2._Object_key 
         and ac2._LogicalDB_key = 1 
         and ac2._MGIType_key = 8 
         and ac2.prefixPart = 'MGI:' 
         order by mgiID desc, term
         ''', 'auto')

#
# Process each row of the results set.
#

fp.write('\n(%d rows affected)\n\n' % (len(results)))
for r in results:
    celltypeTerm = r['celltypeTerm']
    if celltypeTerm == None:
        celltypeTerm = ''
    fp.write("%-9s  %-12s  %-50s  %-35s\n" % (r['jnumID'],r['mgiID'],r['term'],celltypeTerm))
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
