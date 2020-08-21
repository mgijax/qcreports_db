
'''
#
# TR12901
#
# Report:
#	
#       Genotypes with recombinase and conditional ready attributes
#	 but conditional flag set to no
#	1)  genotype has allele with attribute 'recombinase'
#	2)  genotype has allele with attribute 'conditional ready'
#	3)  conditionally targeted flag is no
#
#	Columns:
#       genotype ID
#	Allele MGI ID for recombinase allele(s)
#	Allele MGI ID for conditional ready allele(s)
#
#	Sort: 
#
# Usage:
#       ALL_IncorrectConditional.py
#
# Notes:
#
# History:
#
#	TR12901 sc - created
#
'''
 
import sys 
import os 
import string
import reportlib
import db
import Set

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Genotypes where the conditional flag setting needs review', os.environ['QCOUTPUTDIR'])
#fp.write('\t\texcludes ...\n')

crDict = {}
recDict = {}
genoIdDict = {}
genoDict = {}

fp.write('Genotype ID%sRecombinase Allele ID%sConditional Ready Allele IDs%s' % (TAB, TAB, CRT))

results = db.sql('''select distinct al._Allele_key, a.accid
        from ALL_Allele al, VOC_Annot va, ACC_Accession a
        where al.isWildType = 0
        and al._Allele_key = a._Object_key
        and a._MGIType_key = 11
        and a._LogicalDB_key = 1
        and a.preferred = 1
        and a.prefixPart = 'MGI:'
        and al._Allele_key = va._Object_key
        and va._AnnotType_key = 1014 -- Allele/Subtype
        and va._Term_key = 11025587 --Conditional Ready''', 'auto')
for r in results:
    crDict[r['_Allele_key']] = r['accid']

results = db.sql('''select distinct al._Allele_key, a.accid
        from ALL_Allele al, VOC_Annot va, ACC_Accession a
        where al.isWildType = 0
        and al._Allele_key = a._Object_key
        and a._MGIType_key = 11
        and a._LogicalDB_key = 1
        and a.preferred = 1
        and a.prefixPart = 'MGI:'
        and al._Allele_key = va._Object_key
        and va._AnnotType_key = 1014 -- Allele/Subtype
        and va._Term_key = 11025588 --Recombinase''', 'auto')
for r in results:
    recDict[r['_Allele_key']] = r['accid']

results = db.sql('''select a._Object_key as _Genotype_key, a.accid as genoID
        from ACC_Accession a, GXD_Genotype g
        where a._MGIType_key = 12 --genotype
        and a._LogicalDB_key = 1
        and a.preferred = 1
        and a.prefixPart = 'MGI:'
        and a._Object_key = g._Genotype_key
        and g.isConditional = 0''', 'auto')

for r in results:
        genoIdDict[r['_Genotype_key']] = r['genoID']

results = db.sql('''select ap.*
        from GXD_Genotype g, GXD_AllelePair ap
        where g.isConditional = 0
        and g._genotype_key = ap._Genotype_key''', 'auto')

for r in results:
        genotypeKey = r['_Genotype_key']
        if genotypeKey not in genoDict:
            genoDict[genotypeKey] = []
        genoDict[genotypeKey].append(r)
total = 0
for gKey in genoDict:
    CR = 0
    REC = 0
    alleleDict = {'CR':[], 'REC':[]}
    apList = genoDict[gKey]
    for ap in apList:
        alleleKey1 = ap['_Allele_key_1']
        alleleKey2 = ap['_Allele_key_2']
        if alleleKey1 in crDict:
            CR = 1
            alleleDict['CR'].append(crDict[alleleKey1])
        if alleleKey1 in recDict:
            REC = 1
            alleleDict['REC'].append(recDict[alleleKey1])
        if alleleKey2 in crDict:
            CR = 1
            alleleDict['CR'].append(crDict[alleleKey2])
        if alleleKey2 in recDict:
            REC = 1
            alleleDict['REC'].append(recDict[alleleKey2])
    if CR and REC: # both subtypes found in the genotype
        genoID = genoIdDict[gKey]
        recIds = ', '.join(set(alleleDict['REC']))
        crIds = ', '.join(set(alleleDict['CR']))
        fp.write('%s%s%s%s%s%s' % (genoID, TAB, recIds, TAB, crIds, CRT))
        total += 1

fp.write('%sTotal: %s' % (CRT, total))

reportlib.finish_nonps(fp)
