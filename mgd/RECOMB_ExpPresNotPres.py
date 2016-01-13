#!/usr/local/bin/python

'''
#
# TR 8775: TR 8053/TR 7945
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
#
#       The report should have the following columns:
#
#       1) J Number for the assay
#       2) MGI ID of the assay
#       3) Structure in question
#
# Usage:
#       RECOMB_ExpPresNotPres.py
#
# History:
#
# lec	05/01/2008
#	- new; TR 8775; copy from GXD
#
'''

import sys
import os
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

#
# Open the output file and write a header to it.
#
reportTitle = 'Assays in which the same anatomical structure is annotated as having expression both present and absent'

fp = reportlib.init(sys.argv[0], title = reportTitle, outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Specimens must have the same genotype and age; reproductive system structures are excluded\n\n')
fp.write('J Number   ')
fp.write('MGI ID        ')
fp.write('Structure' + CRT)
fp.write('---------  ')
fp.write('------------  ')
fp.write('----------------------------------------------------------------------------------------------------' + CRT)

#
# structures of male/female reproductive systems are to be excluded
# TS16;urogenital system;gonadal component 
# TS17;urogenital system;gonadal component
# TS18;gonad primordium
# TS19;reproductive system
# TS20;reproductive system
# TS21;reproductive system
# TS22;reproductive system
# TS23;reproductive system
# TS24;reproductive system
# TS25;reproductive system
# TS26;reproductive system
# TS28;reproductive system

db.sql('''
    SELECT DISTINCT c._DescendentObject_key as _Term_key, s._Stage_key
    INTO TEMPORARY TABLE excludeStructs
    FROM VOC_Term t, DAG_Closure c, VOC_Term tt, VOC_Term_EMAPS s
    WHERE t._Vocab_key = 90
      AND t._Term_key = c._AncestorObject_key
      AND c._MGIType_key = 13
      AND c._DescendentObject_key = tt._Term_key
      AND tt._Term_key = s._EMAPA_Term_key
      AND
      (
      (t.term = 'reproductive system' AND s._Stage_key in (19,20,21,22,23,24,25,26,28))
      OR
      (t.term = 'urogenital system' AND s._Stage_key in (16,17))
      OR
      (t.term = 'gonad primordium' AND s._Stage_key in (18))
      )
    UNION 
    SELECT DISTINCT t._Term_key, s._Stage_key
    FROM VOC_TERM t, VOC_Term_EMAPS s
    WHERE t._Vocab_key = 90
      AND t._Term_key = s._EMAPA_Term_key
      AND
      (
      (t.term = 'reproductive system' AND s._Stage_key in (19,20,21,22,23,24,25,26,28))
      OR
      (t.term = 'urogenital system' AND s._Stage_key in (16,17))
      OR
      (t.term = 'gonad primordium' AND s._Stage_key in (18))
      )
	''', None)

db.sql('create index excludeStructs_idx1 on excludeStructs(_Term_key)', None)
db.sql('create index excludeStructs_idx2 on excludeStructs(_Stage_key)', None)

#
# assays with expression
#
db.sql('''
	select distinct e._Assay_key, e._Refs_key, e._EMAPA_Term_key, e._Stage_key, e._Genotype_key, e.age 
	into temporary table expressed 
	from GXD_Expression e 
	where e.isForGXD = 0 
	and e.expressed = 1 
	and not exists (select 1 from excludeStructs r 
		where e._EMAPA_Term_key = r._Term_key and e._Stage_key = r._Stage_key) 
	''', None)
db.sql('create index expressed_idx1 on expressed(_Assay_key)', None)
db.sql('create index expressed_idx2 on expressed(_EMAPA_Term_key)', None)
db.sql('create index expressed_idx3 on expressed(_Stage_key)', None)
db.sql('create index expressed_idx4 on expressed(_Genotype_key)', None)
db.sql('create index expressed_idx5 on expressed(age)', None)

#
# compare expressed/not expressed by assay, structure, genotype, age
#
db.sql('''
	select distinct e.* 
	into temporary table results 
	from expressed e, GXD_Expression n 
	where e._Assay_key = n._Assay_key 
	and n.isForGXD = 0 
	and e._EMAPA_Term_key = n._EMAPA_Term_key 
	and e._Stage_key = n._Stage_key
	and e._Genotype_key = n._Genotype_key 
	and e.age = n.age 
	and n.expressed = 0 
	''', None)
db.sql('create index results_idx1 on results(_Assay_key)', None)
db.sql('create index results_idx2 on results(_EMAPA_Term_key)', None)
db.sql('create index results_idx3 on results(_Stage_key)', None)
db.sql('create index results_idx4 on results(_Refs_key)', None)

#
# final results
#
results = db.sql('''
	select ac1.accID as jnumID, 
	       ac2.accID as mgiID, 
	       t.stage::text || ':' || s.term as term
         from results r, VOC_Term s, GXD_TheilerStage t, ACC_Accession ac1, ACC_Accession ac2 
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
	 order by mgiID, term
	 ''', 'auto')

#
# Process each row of the results set.
#

fp.write('\n(%d rows affected)\n\n' % (len(results)))
for r in results:
    fp.write("%-9s  %-12s  %-100s\n" % (r['jnumID'],r['mgiID'],r['term']))
fp.write('\n(%d rows affected)\n' % (len(results)))

