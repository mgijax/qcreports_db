# requires Python 2.7 for BioPython

'''
#
# ALL_VariantCheckComplement.py
#
# Report variants where for either/both the reference or variant sequence:
#       the sequence is provided for both Transcript and Genomic, and
#       the allele is on the reverse strand, and
#       the transcript sequence is NOT the reverse complement of the 
#		genomic sequence
#
# Requested columns: 
#    Allele ID
#    Allele Symbol 
#
# Usage:
#       ALL_VariantCheckComplement.py
#
# History:
#
# 08/22/2019	sc
#	- TR13115
#
'''

import sys 
import os
import string
import reportlib
import mgi_utils
import db
from Bio.Seq import Seq

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#
    
# {alleleKey:variantKey: {transRef:xx, transVar:xx, genRef:xx, genVar:xx}, ...}
resultsDict = {}

# {alleleKey:alleleID|alleleSymbol, ...}
alleleInfoDict = {}

errorList = []
variantSeqErrorList = []
referenceSeqErrorList = []

# get variant alleles on the minus strand
db.sql(''' select distinct a.symbol, a._Allele_key, av._variant_key
    into temporary table onMinus
    from mrk_location_cache mlc, all_variant av, all_allele a
    where mlc.strand = '-'
    and mlc._marker_key = a._marker_key
   and a._Allele_key = av._allele_key
and av._sourcevariant_key is not null --curated''', None)

db.sql('create index idx2 on onMinus(_Allele_key)', None)

db.sql('create index idx3 on onMinus(_Variant_key)', None)

# create alleleID/symbol lookup by allele key
results = db.sql('''select o._Allele_key, a.accid as alleleID, aa.symbol
    from onMinus o, ACC_Accession a, ALL_Allele aa
    where o._Allele_key = a._Object_key
    and a._MGIType_key = 11
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and o._Allele_key = aa._Allele_key''', 'auto')

for r in results:
    alleleKey = r['_Allele_key']
    alleleID = r['alleleID']
    symbol = r['symbol']
    alleleInfoDict[alleleKey] = '%s|%s' % (alleleID, symbol)

#get dna sequences
resultsD = db.sql('''select distinct o.*,
        vs.referenceSequence, vs.variantSequence
    from onMinus o, all_variant v, all_variant_sequence vs
    where o._allele_key = v._allele_key
    and o._variant_key = vs._variant_key
    and vs._sequence_type_key = 316347 --dna
    order by o.symbol, o._variant_key''', 'auto')

# get rna sequence
resultsR = db.sql('''select distinct o.*,
        vs.referenceSequence, vs.variantSequence
    from onMinus o, all_variant v, all_variant_sequence vs
    where o._allele_key = v._allele_key
    and o._variant_key = vs._variant_key
    and vs._sequence_type_key = 316346 --rna
    order by o.symbol, o._variant_key''', 'auto')

# load genomic data into structure
for r in resultsD:
    alleleKey = r['_Allele_key']
    variantKey = r['_Variant_key']
    dictKey = '%s|%s' % (alleleKey, variantKey)

    genRef =  r['referenceSequence']
    genVar = r['variantSequence']
    if genRef == None and genVar == None:
        continue
    if dictKey not in resultsDict:
        resultsDict[dictKey] = {}
    resultsDict[dictKey]['genRef'] = genRef
    resultsDict[dictKey]['genVar'] = genVar

# load transcript data into structure
for r in resultsR:
    
    alleleKey = r['_Allele_key']
    variantKey = r['_Variant_key']
    dictKey = '%s|%s' % (alleleKey, variantKey)

    transRef =  r['referenceSequence']
    transVar = r['variantSequence']

    if transRef == None and transVar == None:
        continue
    if dictKey not in resultsDict:
        continue # this means we don't have any genomic ref or var sequences
    resultsDict[dictKey]['transRef'] = transRef
    resultsDict[dictKey]['transVar'] = transVar

# now get all the alleles on '-' strand and process
results = db.sql('''select _Allele_key, _Variant_key
        from onMinus''', 'auto')

for r in results:
    alleleKey = r['_Allele_key']
    key = '%s|%s' % (alleleKey, r['_Variant_key'])
    if key in resultsDict:
        seqDict = resultsDict[key]
        # check that transRef is reverse complement genRef
        transRef = ''
        genRef = ''
        transVar = ''
        genVar = ''
        writeError = 0
        if 'transRef' in seqDict and 'genRef' in seqDict:
            transRef = seqDict['transRef']
            genRef = seqDict['genRef']
            genRefCompl = str(Seq(genRef).reverse_complement())
            if transRef != genRefCompl:
                writeError = 1
        # check that transVar is reverse complement genVar
        if 'transVar' in seqDict and 'genVar' in seqDict:
            transVar = seqDict['transVar']
            genVar = seqDict['genVar']
            genVarCompl = str(Seq(genVar).reverse_complement())
            if transVar != genVarCompl:
                writeError = 1
        if writeError:
            alleleInfo = alleleInfoDict[alleleKey]
            id, symbol = str.split(alleleInfo, '|')
            errorList.append('%s%s%s%s%s%s%s%s%s%s%s' % (id, TAB, symbol, TAB, transRef, TAB, genRef, TAB, transVar, TAB, genVar))    


# write to the reports
fp  = reportlib.init(sys.argv[0],  outputdir = os.environ['QCOUTPUTDIR'])
fp.write('The reference or variant transcript sequence is NOT the reverse complement of the reference or variant genomic sequence%s' % CRT)
fp.write('Allele ID%s Symbol%sReference Transcript%sReference Genomic%sVariant Transcript%sVariant Genomic%s' % (TAB, TAB, TAB, TAB, TAB, CRT))
fp.write(CRT.join(errorList))
length = len(errorList)
fp.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

reportlib.finish_nonps(fp)    # non-postscript file
