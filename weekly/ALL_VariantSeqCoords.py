
'''
#
# ALL_VariantSeqCoords.py
#
# Report:
# the as-curated genomic coordinates are (not null and) lie outside the 
#    range of the variant's gene (ie outside its geno
#    mic coordinates) plus or minus some amount (fudge factor TBD)
# the as-curated transcript coordinates are (not null and) lie outside the range
#    [1..length of the transcript whose ID is in the TranscriptID field], or...
# the as-curated protein coordinates are (not null and) lie outside the range 
#    [1..length of the protein whose ID is in the PolypeptideID field] 
#
# Usage:
#       ALL_VariantSeqCoords.py
#
# History:
#
# 08/16/2019	sc
#	- TR13115
#
'''

import sys 
import os
import string
import reportlib
import mgi_utils
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

# get all variant sequences that have start/end coordinates; add the marker
db.sql('''select  a2.accid as alleleID, a.symbol, a._Marker_key, avs.*
    into temporary table variantSeq
    from all_variant av, all_variant_sequence avs, acc_accession a2, all_allele a
    where av._sourcevariant_key is not null --curated
    and av._variant_key = avs._variant_key
    and avs.startCoordinate is not null
    and avs.endCoordinate is not null
        and av._Allele_key = a2._Object_key
    and a2._MGItype_key = 11
    and a2._logicalDB_key = 1
    and a2.preferred = 1
    and a2.prefixPart = 'MGI:'
    and av._Allele_key = a._Allele_key''', None)

db.sql('''create index idx1 on variantSeq(_variantSequence_key)''', None)

########
#  DNA
#######
# get marker coordinates for the alleles' marker
results = db.sql('''select  lc.startCoordinate as markerStart, 
        lc.endCoordinate as markerEnd, t.*
    from variantSeq t, MRK_Location_Cache lc
    where t._Marker_key = lc._Marker_key
    and t._sequence_type_key = 316347 --dna
    order by t.symbol''', 'auto')

# Are the 'as-curated' genomic coordinates outside the range of the variant's genomic coordinates?
genomicRpt = []
for r in results:
    varStart = r['startCoordinate']
    varEnd = r['endCoordinate']
    mrkStart = r['markerStart']
    mrkEnd = r['markerEnd']
    if mrkStart == None or mrkEnd == None:
        continue
    else:
        varStart = int(varStart)
        varEnd = int(varEnd)
        mrkStart = int(mrkStart)
        mrkEnd = int(mrkEnd)
    if varStart < mrkStart or varStart > mrkEnd or varEnd < varStart or varEnd > mrkEnd:
        genomicRpt.append('%s%s%s%s%s%s%s%s%s%s%s' % (r['alleleID'], TAB, r['symbol'], TAB, varStart, TAB, varEnd, TAB, mrkStart, TAB, mrkEnd))


#######
#  RNA
#######

# get rna sequence length
db.sql('''select a.accid as transcriptID, t.*
    into temporary table vTranscripts
    from acc_accession a, variantSeq t
    where t._sequence_type_key = 316346 --rna
        and t._variantSequence_key = a._Object_key
        and a._MGItype_key = 46
        and a.preferred = 1''', 'auto')
db.sql('''create index  idx2 on vTranscripts(transcriptID)''', None)

results = db.sql('''select distinct v.transcriptID, v.startCoordinate, 
        v.alleleID, v.symbol, v.endCoordinate, s.length
    from vTranscripts v, acc_accession a, seq_marker_cache smc, seq_sequence s
    where v.transcriptID = a.accid
    and a._MGItype_key = 19
    and a.preferred = 1
    and a._object_key = smc._sequence_key
    and smc._organism_key = 1
    and smc._sequence_key = s._sequence_key
    order by v.symbol''', 'auto')

# Are the as-curated transcript coordinated outside the length of the transcript
# sequence?
transcriptRpt = []
for r in results:
    varStart = int(r['startCoordinate'])
    varEnd = int(r['endCoordinate'])
    seqLength = int(r['length'])
    if (varEnd - varStart + 1) > seqLength:
        transcriptRpt.append('%s%s%s%s%s%s%s%s%s' % (r['alleleID'], TAB, r['symbol'], TAB, varStart, TAB, varEnd, TAB, seqLength))

#######
#  PROTEIN
#######

# get protein sequence length
db.sql('''select a.accid as proteinID, t.*
    into temporary table vProteins
    from acc_accession a, variantSeq t
    where t._sequence_type_key = 316348 --prot
        and t._variantSequence_key = a._Object_key
        and a._MGItype_key = 46
        and a.preferred = 1''', 'auto')
db.sql('''create index  idx3 on vProteins(proteinID)''', None)

results = db.sql('''select distinct v.proteinID, v.startCoordinate, v.alleleID
        , v.symbol, v.endCoordinate, s.length
    from vProteins v, acc_accession a, seq_marker_cache smc, seq_sequence s
    where v.proteinID = a.accid
    and a._MGItype_key = 19
    and a.preferred = 1
    and a._object_key = smc._sequence_key
    and smc._organism_key = 1
    and smc._sequence_key = s._sequence_key''', 'auto')

proteinRpt = []
for r in results:
    varStart = int(r['startCoordinate'])
    varEnd = int(r['endCoordinate'])
    seqLength = int(r['length'])
    if (varEnd - varStart + 1) > seqLength:
        proteinRpt.append('%s%s%s%s%s%s%s%s%s' % (r['alleleID'], TAB, r['symbol'], TAB, varStart, TAB, varEnd, TAB, seqLength))


# write report
fp1 = reportlib.init(sys.argv[0], fileExt = '.genomic', outputdir = os.environ['QCOUTPUTDIR'])
fp1.write('Variants with curated coordinates outside the variants gene%s%s' %  (CRT, CRT))
fp1.write('Allele ID%s Symbol%sVariant Start%s Variant End%sMarker Start%sMarker End%s' % (TAB, TAB, TAB, TAB, TAB, CRT))
length = len(genomicRpt)
fp1.write(CRT.join(genomicRpt))
fp1.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

fp2 =  reportlib.init(sys.argv[0], fileExt = '.transcript', outputdir = os.environ['QCOUTPUTDIR'])
fp2.write('Variants with curated coordinates inconsistent with the length of the transcript sequence%s%s' % (CRT, CRT))
fp2.write('Allele ID%s Symbol%sVariant Start%s Variant End%sSequence Length%s' % (TAB, TAB, TAB, TAB, CRT))
length = len(transcriptRpt)
fp2.write(CRT.join(transcriptRpt))
fp2.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

fp3 = reportlib.init(sys.argv[0], fileExt = '.protein', outputdir = os.environ['QCOUTPUTDIR'])
fp3.write('Variants with curated coordinates inconsistent with the length of the protein sequence%s%s'% (CRT, CRT))
fp3.write('Allele ID%s Symbol%sVariant Start%s Variant End%sSequence Length%s' % (TAB, TAB, TAB, TAB, CRT))
length = len(proteinRpt)
fp3.write(CRT.join(proteinRpt))
fp3.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

reportlib.finish_nonps(fp1)	# non-postscript file
reportlib.finish_nonps(fp2)
reportlib.finish_nonps(fp3)
