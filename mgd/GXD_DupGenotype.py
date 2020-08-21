
'''
#	TR12255 - this is a rewrite of TR5488 to
#	1. list dup genotypes all on one line
#	2. include isConditional when determining dup
#	3. add column header
#
# 	Tab-delimited format
#	1. comma separated list of duplicate genotype IDs
#	2. comma separated list of allele pairs - each allele pair 
#	    is a '|' delimited set of allele pair attributes
#
#	sc - 2/8/2016 - created
#
'''

import sys
import os
import string
import reportlib
import db
import Set

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'Duplicate Genotypes', os.environ['QCOUTPUTDIR'])


db.sql('''select v.*,  a1.creation_date as genoCreateDate, a1.accid as genoAccid, g.isConditional
    into temporary table allelePair1
    from GXD_AllelePair_View v, ACC_Accession a1, GXD_Genotype g
    where v._Genotype_key = a1._Object_key
    and a1._MGIType_key = 12
    and a1._LogicalDB_key = 1
    and v._Genotype_key = g._Genotype_key''', None)

db.sql('''create index idx1 on allelePair1(_MutantCellLine_key_1)''', None)
db.sql('''create index idx2 on allelePair1(_MutantCellLine_key_2)''', None)

db.sql('''select a.*, c1.cellLine as mcl1
    into temporary table allelePair2
    from allelePair1 a
    left outer join ALL_CellLIne c1 on (a._MutantCellLine_key_1 = c1._CellLine_key)''', None)

db.sql('''select a.*, c2.cellLine as mcl2
    into temporary table allelePair3
    from allelePair2 a
    left outer join ALL_CellLIne c2 on (a._MutantCellLine_key_2 = c2._CellLine_key)''', None)

db.sql('''create index idx3 on allelePair3(_Genotype_key)''', None)

results = db.sql('''select distinct a.*, s._Strain_key, s.strain
    from allelePair3 a, GXD_Genotype g, PRB_Strain s
    where a._Genotype_key = g._Genotype_key
    and g._Strain_key = s._Strain_key''', 'auto')

#{genoAccid:[result1, ...], ...}
genoDict = {}

fp.write('genotypeIds%ssymbol%schr%sallele1%sallele2%salleleState%smcl1%smcl2%sstrain%sisConditional%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT))

# map each genotype ID to its set of allele pairs
for r in results:
    genoAccid = r['genoAccid']
    if genoAccid not in genoDict:
        genoDict[genoAccid]= []
    genoDict[genoAccid].append(r)

#{key:[genoAccid1, ...], ...}
allelePairDict = {}
# create a key  based on all allelePairs for a genotype and map it to 
# all genotype IDs with that  same set of allele pairs
# multiple genotype IDs for the same set of allele pairs are dups
for gId in genoDict:
    keyList = []
    resultsList = genoDict[gId]
    for r in resultsList:
        symbol = r['symbol']
        chr = r['chromosome']
        allele1 = r['allele1']
        allele2 = r['allele2']
        alleleState = r['alleleState']
        mcl1 = r['mcl1']
        mcl2 = r['mcl2']
        if mcl2 == None:
            mcl2 = 'None'	
        strain = r['strain']
        isConditional = r['isConditional']

        # delimit the attributes of each allele pair with '|'
        k = '%s|%s|%s|%s|%s|%s|%s|%s|%s' %(symbol, chr, allele1, allele2, alleleState, mcl1, mcl2, strain, isConditional)
        keyList.append(k)
    # Delimit the allele pairs in the key with 'comma'
    key = ','.join(keyList)
    if key not in allelePairDict:
        allelePairDict[key] = []
    allelePairDict[key].append(gId)

# now look for dups and report them
for key in allelePairDict:
    # if there are multiple records for this key
    if len(allelePairDict[key]) > 1:
        # genotype MGI IDs for this key and write to report
        dupGenoList = allelePairDict[key]
        fp.write('%s%s%s%s' % (', '.join(dupGenoList), TAB, key, CRT))
        
reportlib.finish_nonps(fp) 
