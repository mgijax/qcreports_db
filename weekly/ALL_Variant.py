
'''
#
# ALL_Variant.py
#
# variants associated with phenotypic allels
# Columns for tab-delim report:
#    mgi allele id
#    allele symbol
#    gene symbol
#    chromosome
#    start coordinate
#    end coordinate
#    reference sequence
#    alternative sequence
#    HGVS notation 
#    genome build
#    references, comma delimited
#    curator notes, pipe delimited
#
# Also produces a AGR json format report
#
# Usage:
#       ALL_Variant.py
#
# History:
#
# 08/30/2019	sc
#	- TR13173
#
'''

import sys 
import os
import string
import reportlib
import mgi_utils
import db
import json

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#
jsonList = []

# json example
#{
#  "assembly": "GRCm38", 
#  "genomicReferenceSequence": "T", 
#  "consequence": "SO:0001587", 
#  "references": [
#    {
#      "publicationId": "PMID:25807483"
#    }
#  ], 
#  "chromosome": "17", 
#  "sequenceOfReferenceAccessionNumber": "RefSeq:NC_000083.6", 
#  "end": 75273979, 
#  "alleleId": "MGI:5316784", 
#  "start": 75273979, 
#  "genomicVariantSequence": "A", 
#  "type": "SO:1000008"
#}

# reference lookups
variantPubMedDict = {}
variantJNumDict = {}
variantNoteDict = {}
variantTypeDict = {}
variantEffectDict = {}
contigByChrDict = {
    "1" : "NC_000067.6",
    "2" : "NC_000068.7",
    "3" : "NC_000069.6",
    "4" : "NC_000070.6",
    "5" : "NC_000071.6",
    "6" : "NC_000072.6",
    "7" : "NC_000073.6",
    "8" : "NC_000074.6",
    "9" : "NC_000075.6",
    "10" : "NC_000076.6",
    "11" : "NC_000077.6",
    "12" : "NC_000078.6",
    "13" : "NC_000079.6",
    "14" : "NC_000080.6",
    "15" : "NC_000081.6",
    "16" : "NC_000082.6",
    "17" : "NC_000083.6",
    "18" : "NC_000084.6",
    "19" : "NC_000085.6",
    "X" : "NC_000086.7",
    "Y" : "NC_000087.7",
    "MT": "NC_005089.1"
  }

# get all curated variant references
db.sql('''select mra._Refs_key, mra._Object_key as _Variant_key
    into temporary table variantRefs
    from MGI_Reference_Assoc mra, ALL_Variant v
    where mra._MGIType_key = 45 --variant
    and mra._Object_key = v._Variant_key
    and v._SourceVariant_key is not null''', None)

db.sql('''create index idx1 on variantRefs(_Refs_key)''', None)

# get the pubmed IDs for the curated variant references
results = db.sql('''select a.accid as pubmedID, r.*
    from variantRefs r
    left outer join ACC_Accession a on (a._Object_key = r._Refs_key      
    and a._MGIType_key = 1 and a._LogicalDB_key = 29 and a.preferred = 1)''', 'auto')

for r in results:
    variantKey = r['_Variant_key']
    pubmedID = r['pubmedID']

    if variantKey not in variantPubMedDict:
        variantPubMedDict[variantKey] = []
    if pubmedID != None:
        variantPubMedDict[variantKey].append(pubmedID)

# get the jnumbers for the curated variant references
results = db.sql('''select a.accid as jnumID, r.*
    from variantRefs r
    left outer join ACC_Accession a on (a._Object_key = r._Refs_key
    and a._MGIType_key = 1 and a._LogicalDB_key = 1 and a.preferred = 1 and a.prefixPart = 'J:')''', 'auto')

for r in results:
    variantKey = r['_Variant_key']
    jnumID = r['jnumID']
    if variantKey not in variantJNumDict:
        variantJNumDict[variantKey] = []
    if jnumID != None:
        variantJNumDict[variantKey].append(jnumID)

# variant curator notes lookup
variantNoteDict = {}
results = db.sql('''select n._Object_key as _Variant_key, nc.note
    from MGI_Note n, MGI_NoteChunk nc, ALL_Variant v
    where n._NoteType_key = 1050
    and n._Note_key = nc._Note_key
    and n._Object_key = v._Variant_key
    and v._SourceVariant_key is not null''', 'auto')
for r in results:
    variantKey = r['_Variant_key']
    note = str.strip(r['note'])
    note = str.replace(note, '\n', ' ')
    if variantKey not in variantNoteDict:
        variantNoteDict[variantKey] = []
    variantNoteDict[variantKey].append(note)

# variant type annotations (SO IDs)
results = db.sql('''select distinct v._variant_key, aa.accid
  from
      all_variant v, voc_annot va, voc_term vt, acc_accession aa
  where v._variant_key = va._object_key
      and va._annottype_key = 1026
      and va._term_key = vt._term_key
      and vt._term_key = aa._object_key
      and aa._mgitype_key = 13
      and aa.preferred = 1
  order by v._variant_key''', 'auto')

for r in results:
    variantKey = r['_variant_key']
    soID = r['accid']
    if variantKey not in variantTypeDict:
        variantTypeDict[variantKey] = []
    variantTypeDict[variantKey].append(soID)

# variant effect annotations (SO IDs)
results = db.sql('''select distinct v._variant_key, aa.accid
  from
      all_variant v, voc_annot va, voc_term vt, acc_accession aa
  where v._variant_key = va._object_key
      and va._annottype_key = 1027
      and va._term_key = vt._term_key
      and vt._term_key = aa._object_key
      and aa._mgitype_key = 13
      and aa.preferred = 1
  order by v._variant_key''', 'auto')

for r in results:
    variantKey = r['_variant_key']
    soID = r['accid']
    if variantKey not in variantEffectDict:
        variantEffectDict[variantKey] = []
    variantEffectDict[variantKey].append(soID)

# alleles with phenotype annotations MP annot Type 1002
db.sql('''select ap._Allele_key_1 as _allele_key
    into temporary table mp
    from GXD_AllelePair ap, GXD_Genotype g, VOC_Annot va
    where ap._Genotype_key = g._Genotype_key
    and g._Genotype_key = va._Object_key
    and va._Annottype_key = 1002
union
    select ap._Allele_key_2 as _allele_key
    from GXD_AllelePair ap, GXD_Genotype g, VOC_Annot va
    where ap._Genotype_key = g._Genotype_key
    and g._Genotype_key = va._Object_key
    and va._Annottype_key = 1002''', None)
#    and va._Term_key = 83412 --no abnormal phenotype detected''', None)

db.sql('create index idx2 on mp(_Allele_key)', None)

# above that have variants
db.sql('''select distinct av._Variant_key, av.description, av._Allele_key
    into temporary table variants
    from ALL_Variant av, mp
    where av._SourceVariant_key is not null
    and av._Allele_key = mp._Allele_key''', None)

db.sql('''create index idx3 on variants(_Variant_key)''', None)

results = db.sql('''select distinct vs._variantsequence_key, a.accid as alleleID, 
        aa.symbol as alleleSymbol, m.symbol as markerSymbol, m.chromosome, 
        vs.startCoordinate, vs.endCoordinate, vs.referenceSequence, 
        vs.variantSequence , vs.version, v.description as hgvs, v._Variant_key
    from variants v, ACC_Accession a, ALL_Allele aa, MRK_Marker m, 
        ALL_Variant_Sequence vs
    where v._Allele_key = a._Object_key
    and a._MGIType_key = 11
    and a.preferred = 1
    and a._LogicalDB_key = 1
    and a.prefixPart = 'MGI:'
    and v._Allele_key = aa._Allele_key
    and aa._Marker_key = m._Marker_key 
    and v._Variant_key = vs._Variant_key
    and vs._sequence_type_key = 316347 --dna
    order by vs._variantsequence_key''', 'auto')
    #order by a.accid''', 'auto')

 
# write to the reports
fp  = reportlib.init(sys.argv[0], title = 'Sequence variants associated with phenotypic alleles', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fpJson = reportlib.init(sys.argv[0], fileExt = '.json.rpt', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('Allele ID%sAllele Symbol%sGene Symbol%sChromosome%sStart Coordinate%sEnd Coordinate%sReference Sequence%sVariant Sequence%sHGVS%sGenome Build%sPubMed IDs%sJNum IDs%sCurator Note%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT))
length = len(results)


for r in results:
    alleleID = r['alleleID']
    alleleSymbol = r['alleleSymbol']
    markerSymbol = r['markerSymbol']
    start =  r['startCoordinate']
    if start == None:
        start = ''
    else:
        start = int(start)

    end = r['endCoordinate']
    if end == None:
        end = ''
    else:
        end = int(end)

    refSeq = r['referenceSequence']
    if refSeq == None:
        refSeq = ''
    else:
        refSeq = str.strip(refSeq)

    varSeq =  r['variantSequence']
    if varSeq == None:
        varSeq = ''
    else:
        varSeq = str.strip(varSeq)

    hgvs = r['hgvs']
    if hgvs == None:
        hgvs = ''
    else:
        hgvs = str.strip(hgvs)
    version = r['version']
    if version == None:
        version = ''
    else:
        version = str.strip(version)

    variantKey = r['_Variant_key']

    pubMedIDList = []
    if variantKey in variantPubMedDict:
        pubMedIDList = variantPubMedDict[variantKey]
    pubMedString = ', '.join(pubMedIDList)

    jnumIDList = []
    if variantKey in variantJNumDict:
        jnumIDList = variantJNumDict[variantKey]
    jnumString = ', '.join(jnumIDList)

    noteList = []
    if variantKey in variantNoteDict:
         noteList = variantNoteDict[variantKey]
    noteString = '|||'.join(noteList)

    typeList = []
    if variantKey in variantTypeDict:
        typeList =  variantTypeDict[variantKey]
    typeString = ', '.join(typeList)

    effectList = []
    if variantKey in variantEffectDict:
        effectList = variantEffectDict[variantKey]
    effectString = ', '.join(effectList)

    chromosome = r['chromosome']
    contig = ''
    if chromosome in  contigByChrDict:
        contig = contigByChrDict[chromosome]

    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (alleleID, TAB, alleleSymbol, TAB, markerSymbol, TAB, chromosome, TAB, start, TAB, end, TAB, refSeq, TAB, varSeq, TAB, hgvs, TAB, version, TAB, pubMedString, TAB, jnumString, TAB, noteString, CRT))
    currentDict = {}

    contigACC = "RefSeq:%s" % contig
    refList = []
    for id in pubMedIDList:
        currentRefDict = {}
        currentRefDict["publicationId"] = "PMID:%s" % id
        refList.append(currentRefDict)

    currentDict["alleleId"] = "%s" % alleleID
    currentDict["assembly"] = "%s" % version
    currentDict["chromosome"] = "%s" % chromosome
    currentDict["sequenceOfReferenceAccessionNumber"] = contigACC
    currentDict["start"] = start
    currentDict["end"] = end
    currentDict["genomicReferenceSequence"] = "%s" % refSeq
    currentDict["genomicVariantSequence"] = "%s" % varSeq
    currentDict["consequence"] = "%s" % effectString
    currentDict["type"] = "%s" % typeString
    currentDict["references"] = refList
    try:
        jsonString = json.dumps(currentDict)
        jsonList.append(jsonString)
    except:
        print('not able to serialize currentDict')

fp.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))
fpJson.write('[%s]' % ', '.join(jsonList))

reportlib.finish_nonps(fp)    # non-postscript file
reportlib.finish_nonps(fpJson)    # non-postscript file
