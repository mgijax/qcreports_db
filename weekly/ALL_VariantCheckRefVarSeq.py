#!/opt/python/bin/python

'''
#
# ALL_VariantCheckRefVarSeq.py
#
# Report:
#
# Report where genomic reference sequence is the same as variant sequence
# Columns:
#   1. AlleleID
#   2. AlleleSymbol
#   3. CuratedGenomicReferenceAllele
#   4. CuratedGenomicVariantAllele
#   5. CuratorNotes
#
# Usage:
#       ALL_VariantCheckRefVarSeq.py
#
# History:
#
# 05/13/2020	sc
#	- TR13265
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

fp  = reportlib.init(sys.argv[0], title = 'Variants where reference and variant sequence are the same', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('AlleleID%sAlleleSymbol%sRef%sVar%sCuratorNotes%s' % (TAB, TAB, TAB, TAB, CRT))
db.sql('''select aa.accid, a.symbol, vs.referencesequence, 
        vs.variantsequence, vs._variant_key
    into temporary table variants
    from acc_accession aa, all_variant v, all_variant_sequence vs, all_allele a
    where v._sourceVariant_key is not null --curated
    and v._variant_key = vs._variant_key
    and vs._sequence_type_key = 316347
    and vs.referencesequence = vs.variantsequence
    and v._allele_key = a._allele_key
    and v._allele_key = aa._object_key
    and aa._mgitype_key = 11
    and aa._Logicaldb_key = 1
    and aa.preferred = 1
    and aa.prefixpart = 'MGI:' ''', None)

db.sql('''create index idx1 on variants(_variant_key)''')

db.sql('''select n._object_key, nc.note
    into temporary table variantNotes
    from MGI_Note n, MGI_NoteChunk nc
    where n._NoteType_key = 1050
    and n._note_key = nc._note_key''', None)

db.sql('''create index idx2 on variantNotes(_object_key)''', None)

results = db.sql('''select v.*, vn.note
    from variants v
    left outer join variantNotes vn on (v._variant_key = vn._object_key)''', 'auto')

for r in results:
    curNote = r['note']
    if curNote == None:
        curNote = ''
    fp.write('%s%s%s%s%s%s%s%s%s%s' % (r['accid'], TAB, r['symbol'], TAB, r['referencesequence'], TAB, r['variantsequence'], TAB, curNote, CRT) )
reportlib.finish_nonps(fp)	# non-postscript file
