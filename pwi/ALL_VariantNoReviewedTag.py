
'''
#
# Variants no reviewed tag
#
# Minimal Information: 
#       1. It has curated genomic coordinates 
#       2. It has ref and var seqs 
#       3. It has types and effects
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

db.sql('''
select al.symbol as alleleSymbol, 
aa.accid as alleleID, 
vs._variant_key, 
vs.startCoordinate as start, 
vs.endCoordinate as end, 
vs.referenceSequence as reference, 
vs.variantSequence as variant, 
u.name as createdBy 
into temporary table curatedNotReviewed 
from all_variant av, all_variant_sequence vs, all_allele al, acc_accession aa, mgi_user u 
where av._sourceVariant_key is not null 
and av.isReviewed = 0 
and av._createdby_key = u._user_key 
and av._variant_key = vs._variant_key 
and vs._sequence_type_key = 316347 /*genomic*/ 
and vs.startCoordinate is not null 
and vs.endCoordinate is not null 
and vs.referenceSequence is not null 
and vs.variantSequence is not null 
and av._allele_key = al._allele_key 
and al._allele_key = aa._object_key 
and aa._mgitype_key = 11 
and aa._logicaldb_key = 1 
and aa.preferred = 1 
and aa.prefixPart = 'MGI:'
''', None)

db.sql('create index idx1 on curatedNotReviewed(_variant_key)', None)

db.sql('''
select n._object_key as _variant_key, n.note 
into temporary table curatorNotes 
from MGI_Note n 
where n._noteType_key = 1050
''', None)

db.sql('create index idx2 on curatorNotes(_variant_key)', None)

results = db.sql('''
select 
cnr.alleleSymbol, 
cnr.alleleID, 
cnr.start, 
cnr.end, 
cnr.reference, 
cnr.variant, 
cnr.createdBy, 
cn.note as curatorNote 
from curatedNotReviewed cnr left outer join curatorNotes cn on(cnr._variant_key = cn._variant_key) 
order by cnr.alleleSymbol
''', 'auto')

sys.stdout.write('alleleSymbol' + TAB)
sys.stdout.write('alleleID' + TAB)
sys.stdout.write('start' + TAB)
sys.stdout.write('end' + TAB)
sys.stdout.write('reference' + TAB)
sys.stdout.write('variant' + TAB)
sys.stdout.write('createdBy' + TAB)
sys.stdout.write('curatorNote' + CRT)

for r in results:
        sys.stdout.write(r['alleleSymbol'] + TAB)
        sys.stdout.write(r['alleleID'] + TAB)
        sys.stdout.write(str(r['start']) + TAB)
        sys.stdout.write(str(r['end']) + TAB)
        sys.stdout.write(r['reference'] + TAB)
        sys.stdout.write(r['variant'] + TAB)
        sys.stdout.write(r['createdBy'] + TAB)

        if r['curatorNote'] == None:
                sys.stdout.write(CRT)
        else:
                note = r['curatorNote'].replace('\n', ' ').replace('\t', ' ')
                sys.stdout.write(note + CRT)

sys.stdout.flush()

