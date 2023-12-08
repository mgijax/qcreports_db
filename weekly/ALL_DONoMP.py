
'''
#
# ALL_DONoMP.py
#
# Report:
#
#       Alleles with DO annotations, but no MP annotation
#
# Usage:
#       ALL_DONoMP.py
#
# Notes:
#
# History:
#
# sc   08/30/2016
#       - created TR 12022
'''

import sys
import os
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'Alleles with DO annotations but no MP', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Genotype ID%sDO ID%sJ:%s%s' % (TAB, TAB, CRT, CRT))

# Alleles with DO annotations
db.sql('''select a._Object_key as _Genotype_key, a._Term_key as termKey, e._Refs_key
    into temporary table doalleles
    from VOC_Annot a, VOC_Evidence e, GXD_AllelePair ap
    where a._AnnotType_key in (1020)
    and a._Annot_key = e._Annot_key
    and a._Object_key = ap._Genotype_key''', None)

# Alleles with MP Annotations 
db.sql('''select a._Object_key as _Genotype_key, a._Term_key as termKey, e._Refs_key
    into temporary table mpalleles
    from VOC_Annot a, VOC_Evidence e, GXD_AllelePair ap
    where a._AnnotType_key = 1002
    and a._Annot_key = e._Annot_key
    and a._Object_key = ap._Genotype_key''', None)

# Alleles with DO, no MP annotations
db.sql('''select *
    into temporary table nomp
    from doalleles o
    where not exists(select 1
    from mpalleles m
    where o._Genotype_key = m._Genotype_key)''', None)

# resolve keys to IDs
results = db.sql('''select a1.accid as mgiID, a2.accid as jNum, 
        a3.accid as termID
    from nomp n, ACC_Accession a1, ACC_Accession a2, ACC_Accession a3
    where n._Genotype_key = a1._Object_key
    and a1._MGIType_key = 12 /* GXD_Genotype */
    and a1._LogicalDB_key = 1 /* MGI */
    and a1.preferred = 1
    and a1.prefixPart = 'MGI:'
    and n._Refs_key = a2._Object_key
    and a2._MGIType_key = 1 /* BIB_Refs */
    and a2._LogicalDB_key = 1 /* MGI */
    and a2.preferred = 1
    and a2.prefixPart = 'J:'
    and n.termKey = a3._Object_key
    and a3._MGIType_key = 13 /* VOC_Term */
    and a3._LogicalDB_key in (191) /* DO */
    and a3.preferred = 1''', 'auto')

for r in results:
    genotypeID = r['mgiID']
    termID = r['termID']
    jNum = r['jNum']
    fp.write('%s%s%s%s%s%s' % ( genotypeID, TAB, termID, TAB, jNum, CRT ))
   
reportlib.finish_nonps(fp)
