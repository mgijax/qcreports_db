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
# TS16;urogenital system;gonadal component [1787]
# TS17;urogenital system;gonadal component [2378]
# TS18;gonad primordium [3000]
# TS19;reproductive system [3715]
# TS20;reproductive system [4402]
# TS21;reproductive system [5261]
# TS22;reproductive system [6327]
# TS23;reproductive system [7648]
# TS24;reproductive system [7649]
# TS25;reproductive system [7650]
# TS26;reproductive system [7651]
# TS28;reproductive system [6950]

db.sql('''
	select _Descendent_key as _Structure_key
	into temporary table excludeStructs 
	from GXD_StructureClosure 
	where _Structure_key in (1787,2378,3000,3715,4402,5261,6327,7648,7649,7650,7651,6950)
	''', None)
db.sql('create index excludeStruct_idx1 on excludeStructs(_Structure_key)', None)

#
# assays with expression
#
db.sql('''
	select distinct e._Assay_key, e._Refs_key, e._Structure_key, e._Genotype_key, e.age 
	into temporary table expressed 
	from GXD_Expression e 
	where e.isForGXD = 0 
	and e.expressed = 1 
	and not exists (select 1 from excludeStructs r where e._Structure_key = r._Structure_key) 
	''', None)
db.sql('create index expressd_idx1 on expressed(_Assay_key)', None)
db.sql('create index expressd_idx2 on expressed(_Structure_key)', None)
db.sql('create index expressd_idx3 on expressed(_Genotype_key)', None)
db.sql('create index expressd_idx4 on expressed(age)', None)

#
# compare expressed/not expressed by assay, structure, genotype, age
#
db.sql('''
	select distinct e.* 
	into temporary table results 
	from expressed e, GXD_Expression n 
	where e._Assay_key = n._Assay_key 
	and n.isForGXD = 0 
	and e._Structure_key = n._Structure_key 
	and e._Genotype_key = n._Genotype_key 
	and e.age = n.age 
	and n.expressed = 0 
	''', None)
db.sql('create index results_idx1 on results(_Assay_key)', None)
db.sql('create index results_idx2 on results(_Structure_key)', None)
db.sql('create index results_idx3 on results(_Refs_key)', None)

#
# final results
#
results = db.sql('''
	select ac1.accID as jnumID, 
	       ac2.accID as mgiID, 
	       convert(varchar(2), t.stage) || ':' || s.printName as structure
         from results r, GXD_Structure s, GXD_TheilerStage t, ACC_Accession ac1, ACC_Accession ac2 
         where r._Structure_key = s._Structure_key 
         and s._Stage_key = t._Stage_key 
         and r._Refs_key = ac1._Object_key 
         and ac1._LogicalDB_key = 1 
         and ac1._MGIType_key = 1 
         and ac1.prefixPart = 'J:' 
         and r._Assay_key = ac2._Object_key 
         and ac2._LogicalDB_key = 1 
         and ac2._MGIType_key = 8 
         and ac2.prefixPart = 'MGI:' 
         order by mgiID
	 ''', 'auto')

#
# Process each row of the results set.
#

fp.write('\n(%d rows affected)\n\n' % (len(results)))
for r in results:
    fp.write("%-9s  %-12s  %-100s\n" % (r['jnumID'],r['mgiID'],r['structure']))
fp.write('\n(%d rows affected)\n' % (len(results)))

