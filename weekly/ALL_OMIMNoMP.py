#!/usr/local/bin/python

'''
#
# ALL_OMIMNoMP.py
#
# Report:
#
#       Alleles with OMIM annotations, but no MP annotation
#
# Usage:
#       ALL_OMIMNoMP.py
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
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'Alleles with OMIM annotations but no MP', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Genotype ID%sOMIM ID%sJNum%s' % (TAB, TAB, CRT))

# Genotype OMIM annotations can have > reference
omimDict = {}

# Alleles with OMIM annotations
db.sql('''select a._Object_key as _Genotype_key, a._Term_key as omimKey, 
	e._Refs_key
    into temporary table omimalleles
    from VOC_Annot a, VOC_Evidence e, GXD_AllelePair ap
    where a._AnnotType_key = 1005
    and a._Annot_key = e._Annot_key
    and a._Object_key = ap._Genotype_key''', None)

# Alleles with MP Annotations 
db.sql('''select a._Object_key as _Genotype_key, a._Term_key as omimKey, 
	e._Refs_key
    into temporary table mpalleles
    from VOC_Annot a, VOC_Evidence e, GXD_AllelePair ap
    where a._AnnotType_key = 1002
    and a._Annot_key = e._Annot_key
    and a._Object_key = ap._Genotype_key''', None)

# Alleles with OMIM, no MP annotations
db.sql('''select *
    into temporary table nomp
    from omimalleles o
    where not exists(select 1
    from mpalleles m
    where o._Genotype_key = m._Genotype_key)''', None)

# resolve keys to IDs
results = db.sql('''select a1.accid as mgiID, a2.accid as jNum, 
	a3.accid as omimID
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
    and n.omimKey = a3._Object_key
    and a3._MGIType_key = 13 /* VOC_Term */
    and a3._LogicalDB_key = 15 /* OMIM */
    and a3.preferred = 1''', 'auto')

for r in results:
    genotypeID = r['mgiID']
    omimID = r['omimID']
    jNum = r['jNum']
    key = '%s|%s' % (genotypeID, omimID)
    if key not in omimDict:
	omimDict[key] = []
    omimDict[key].append(jNum)
   
for key in omimDict:
    print key
    genotypeID, omimID = string.split(key, '|')
    refList = omimDict[key] 
    print refList
    fp.write('%s%s%s%s%s%s' % ( genotypeID, TAB, omimID, TAB, ','.join(refList), CRT ))

reportlib.finish_nonps(fp)
