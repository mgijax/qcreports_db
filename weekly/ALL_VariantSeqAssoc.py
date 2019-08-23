#!/usr/local/bin/python

'''
#
# ALL_VariantSeqAssoc.py
#
# Report:
# 
# the as-curated transcript or protein ID is not associated with the 
#     variant's corresponding Marker.
# the as-curated transcript or protein ID is associated with a different 
#     marker than the variant's corresponding marker.
# Requested columns: 
#    Allele ID
#    Allele Symbol
#    Marker Symbol the ID is associated with 
# Usage:
#       ALL_VariantSeqAssoc.py
#
# History:
#
# 08/19/2019	sc
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

###
# Transcript Lookups
###

# markers associated with variant transcripts
mrkTranscriptDict = {}

# get all variant sequence sequence IDs
db.sql('''select a.accid as transcriptID
    into temporary table vTranscripts
    from all_variant_sequence avs, acc_accession a
    where avs._sequence_type_key = 316346 --rna
      and avs._variantSequence_key = a._Object_key
      and a._MGItype_key = 46
      and a.preferred = 1''', 'auto')

db.sql('''create index  idx4 on vTranscripts(transcriptID)''', None)

results = db.sql('''select distinct v.transcriptID, m.symbol
    from vTranscripts v, acc_accession a, seq_marker_cache smc, mrk_marker m
    where v.transcriptID = a.accid
    and a._MGItype_key = 19
    and a.preferred = 1
    and a._object_key = smc._sequence_key
    and smc._organism_key = 1
    and smc._marker_key = m._marker_key''', 'auto')
print 'loading mrkTranscriptDict'
for r in results:
    t = string.strip(r['transcriptID'])
    s = string.strip(r['symbol'])
    print '"%s":"%s"' % (t, s)
    if t not in mrkTranscriptDict:
	mrkTranscriptDict[t] = []
    mrkTranscriptDict[t].append(s)

###
# Protein Lookups
###

# markers associated with variant proteins
mrkProteinDict = {}

# get all variant sequence sequence IDs
db.sql('''select a.accid as proteinID
    into temporary table vProteins
    from all_variant_sequence avs, acc_accession a
    where avs._sequence_type_key = 316348 --prot
        and avs._variantSequence_key = a._Object_key
        and a._MGItype_key = 46
        and a.preferred = 1''', 'auto')
db.sql('''create index  idx5 on vProteins(proteinID)''', None)

results = db.sql('''select distinct v.proteinID, m.symbol
    from vProteins v, acc_accession a, seq_marker_cache smc, mrk_marker m
    where v.proteinID = a.accid
    and a._MGItype_key = 19
    and a.preferred = 1
    and a._object_key = smc._sequence_key
    and smc._organism_key = 1
    and smc._marker_key = m._marker_key''', 'auto')
print 'loading mrkProteinDict'
for r in results:
    t = string.strip(r['proteinID'])
    s = string.strip(r['symbol'])
    print '"%s":"%s"' % (t, s)
    if t not in mrkProteinDict:
        mrkProteinDict[t] = []
    mrkProteinDict[t].append(s)

# get all variant sequences with the variant markers
db.sql('''select  aa.accid as alleleID, a.symbol as asymbol, m.symbol as msymbol, m._marker_key, avs.*
    into temporary table variantSeq
    from all_variant av, all_variant_sequence avs, acc_accession aa, all_allele a, mrk_marker m
    where av._sourcevariant_key is not null --curated
    and av._variant_key = avs._variant_key
    and av._Allele_key = aa._Object_key
    and aa._MGItype_key = 11
    and aa._logicalDB_key = 1
    and aa.preferred = 1
    and aa.prefixPart = 'MGI:'
    and av._Allele_key = a._Allele_key
    and a._Marker_key = m._Marker_key''', None)

db.sql('''create index idx6 on variantSeq(_variantSequence_key)''', None)

# the as-curated transcript ID is not associated with the variant's 
#    corresponding Marker. 
transNotAssocRpt = []

# the as-curated transcript ID is associated with a different marker
transDiffMrkRpt = []
#######
#  RNA
#######
results = db.sql('''select a1.accid as transcriptID, m.symbol as msymbol, vs.*
    from variantSeq vs, acc_accession a1, mrk_marker m
    where vs._sequence_type_key = 316346 --rna
    and vs._variantSequence_key = a1._Object_key
    and a1._MGItype_key = 46
    and a1.preferred = 1
    and vs._Marker_key = m._Marker_key''', 'auto')

for r in results:
    transcriptID = r['transcriptID']
    alleleID = r['alleleID']
    alleleSymbol = r['asymbol']
    markerSymbol = r['msymbol']
    print '"%s", "%s", "%s", "%s"' % (transcriptID, alleleID, alleleSymbol, markerSymbol)
    if transcriptID in mrkTranscriptDict:
	print '%s in mrkTranscriptDict %s' % (transcriptID, mrkTranscriptDict[transcriptID])
	# transcript assoc with different marker
	if markerSymbol not in mrkTranscriptDict[transcriptID]:
	    print '%s not same as %s' % (markerSymbol, mrkTranscriptDict[transcriptID])
	    transDiffMrkRpt.append('%s%s%s%s%s%s%s%s%s' % (transcriptID, TAB, alleleID, TAB, alleleSymbol, TAB, markerSymbol, TAB, string.join(mrkTranscriptDict[transcriptID], ', ')))
	    
    else: # transcript no assoc w/any marker
	print '%s Not in mrkTranscriptDict' % transcriptID
	transNotAssocRpt.append('%s%s%s%s%s%s%s%s%s' % (transcriptID, TAB, alleleID, TAB, alleleSymbol, TAB, markerSymbol, TAB, ''))

#######
#  PROTEIN
#######
# the as-curated protein ID is not associated with the variant's
#    corresponding Marker.
protNotAssocRpt = []

# the as-curated protein ID is associated with a different marker
protDiffMrkRpt = []

results = db.sql('''select a1.accid as proteinID, m.symbol as msymbol, vs.*
    from variantSeq vs, acc_accession a1, mrk_marker m
    where vs._sequence_type_key = 316348 --prot
    and vs._variantSequence_key = a1._Object_key
    and a1._MGItype_key = 46
    and a1.preferred = 1
    and vs._Marker_key = m._Marker_key''', 'auto')

for r in results:
    proteinID = r['proteinID']
    alleleID = r['alleleID']
    alleleSymbol = r['asymbol']
    markerSymbol = r['msymbol']
    print '"%s", "%s", "%s", "%s"' % (proteinID, alleleID, alleleSymbol, markerSymbol)
    if proteinID in mrkProteinDict:
        print '%s in mrkProteinDict %s' % (proteinID, mrkProteinDict[proteinID])
        # protein assoc with different marker
        if markerSymbol not in mrkProteinDict[proteinID]:
            print '%s not same as %s' % (markerSymbol, mrkProteinDict[proteinID])
            protDiffMrkRpt.append('%s%s%s%s%s%s%s%s%s' % (proteinID, TAB, alleleID, TAB, alleleSymbol, TAB, markerSymbol, TAB, string.join(mrkProteinDict[proteinID], ', ')))

    else: # protein no assoc w/any marker
        print '%s Not in mrkProteinDict' % proteinID
        protNotAssocRpt.append('%s%s%s%s%s%s%s%s%s' % (proteinID, TAB, alleleID, TAB, alleleSymbol, TAB, markerSymbol, TAB, ''))

# write report
fp1 = reportlib.init(sys.argv[0], fileExt = '.transcript', outputdir = os.environ['QCOUTPUTDIR'])
fp1.write('Variants where transcript ID not associated with the variants marker%s%s' %  (CRT, CRT))
fp1.write('Transcript ID%sAllele ID%sSymbol%sVariant Marker%s%s' % (TAB, TAB, TAB, TAB, CRT))
length = len(transNotAssocRpt)
fp1.write(string.join(transNotAssocRpt, CRT))
fp1.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

fp1.write('Variants where transcript ID associated with a different marker%s%s' % (CRT, CRT))
fp1.write('Transcript ID%sAllele ID%sSymbol%sVariant Marker%sTranscript Marker%s' % (TAB, TAB, TAB, TAB, CRT))
length = len(transDiffMrkRpt)
fp1.write(string.join(transDiffMrkRpt, CRT))
fp1.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

fp2 = reportlib.init(sys.argv[0], fileExt = '.protein', outputdir = os.environ['QCOUTPUTDIR'])
fp2.write('Variants where protein ID not associated with the variants marker%s%s'% (CRT, CRT))
fp2.write('Protein ID%sAllele ID%sSymbol%sVariant Marker%s%s' % (TAB, TAB, TAB, TAB, CRT))
length = len(protNotAssocRpt)
fp2.write(string.join(protNotAssocRpt, CRT))
fp2.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

fp2.write('Variants where protein ID associated with a different marker%s%s' % (CRT, CRT))
fp2.write('Protein ID%sAllele ID%sSymbol%sVariant Marker%sProtein Marker%s' % (TAB, TAB, TAB, TAB, CRT))
length = len(protDiffMrkRpt)
fp2.write(string.join(protDiffMrkRpt, CRT))
fp2.write('%sTotal: %s%s%s' % (CRT, length, CRT, CRT))

reportlib.finish_nonps(fp1)	# non-postscript file
reportlib.finish_nonps(fp2)

