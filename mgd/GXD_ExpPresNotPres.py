#!/usr/local/bin/python

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
#          J:50869, J:91257, J:93500, J:93300, J:99307.
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
# lec	12/07/2006
#	- TR 8053; converted to QC report
#
# dbm    11/6/2006    created
#
'''

import sys
import os
import db
import reportlib

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

# excluded references
db.sql('select _Refs_key = a._Object_key into #excludeRefs ' + \
	'from ACC_Accession a ' + \
        'where a._MGIType_key = 1 ' + \
        'and a._LogicalDB_key = 1 ' + \
        'and a.accID in ("J:46439","J:50869","J:91257","J:93500","J:93300","J:99307")', None)
db.sql('create index idx1 on #excludeRefs(_Refs_key)', None)

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

db.sql('select _Structure_key = _Descendent_key ' + \
	'into #excludeStructs ' + \
	'from GXD_StructureClosure ' + \
	'where _Structure_key in (1787,2378,3000,3715,4402,5261,6327,7648,7649,7650,7651,6950)', None)
db.sql('create index idx1 on #excludeStructs(_Structure_key)', None)

#
# assays with expression
#
db.sql('select distinct e._Assay_key, e._Refs_key, e._Structure_key, e._Genotype_key, e.age ' + \
	'into #expressed ' + \
	'from GXD_Expression e ' + \
	'where e.expressed = 1 ' + \
	'and not exists (select 1 from #excludeStructs r where e._Structure_key = r._Structure_key) ' + \
	'and not exists (select 1 from #excludeRefs r where e._Refs_key = r._Refs_key)', None)
db.sql('create index idx1 on #expressed(_Assay_key)', None)
db.sql('create index idx2 on #expressed(_Structure_key)', None)
db.sql('create index idx3 on #expressed(_Genotype_key)', None)
db.sql('create index idx4 on #expressed(age)', None)

#
# compare expressed/not expressed by assay, structure, genotype, age
#
db.sql('select distinct e.* ' + \
	'into #results ' + \
	'from #expressed e, GXD_Expression n ' + \
	'where e._Assay_key = n._Assay_key ' + \
	'and e._Structure_key = n._Structure_key ' + \
	'and e._Genotype_key = n._Genotype_key ' + \
	'and e.age = n.age ' + \
	'and n.expressed = 0 ', None)
db.sql('create index idx1 on #results(_Assay_key)', None)
db.sql('create index idx2 on #results(_Structure_key)', None)
db.sql('create index idx3 on #results(_Refs_key)', None)

#
# final results
#
results = db.sql('select jnumID = ac1.accID , mgiID = ac2.accID, structure = convert(varchar(2), t.stage) + ":" + s.printName ' + \
         'from #results r, GXD_Structure s, GXD_TheilerStage t, ACC_Accession ac1, ACC_Accession ac2 ' + \
         'where r._Structure_key = s._Structure_key ' + \
         'and s._Stage_key = t._Stage_key ' + \
         'and r._Refs_key = ac1._Object_key ' + \
         'and ac1._LogicalDB_key = 1 ' + \
         'and ac1._MGIType_key = 1 ' + \
         'and ac1.prefixPart = "J:" ' + \
         'and r._Assay_key = ac2._Object_key ' + \
         'and ac2._LogicalDB_key = 1 ' + \
         'and ac2._MGIType_key = 8 ' + \
         'and ac2.prefixPart = "MGI:" ' + \
         'order by mgiID', 'auto')

#
# Process each row of the results set.
#
for r in results:
    fp.write("%-9s  %-12s  %-100s\n" % (r['jnumID'],r['mgiID'],r['structure']))
fp.write('\n(%d rows affected)\n' % (len(results)))

