
'''
#
# Variants needing HGVS data
#
# Report variants where: 
#       HGVS field is null 
#       all five curated genomic fields are not null 
#       Columns: 
#               Allele ID 
#               Allele Symbol 
#               Chromosome 
#               curated genomic Start 
#               curated genomic Reference Allele 
#               curated genomic Variant Allele
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
select v._Allele_key, s.* 
into temporary table noDescription 
from ALL_Variant v, ALL_Variant_Sequence s 
where v._sourcevariant_key is not null 
and v.description is null 
and v._Variant_key = s._Variant_key 
and s._Sequence_type_key = 316347 --dna 
and s.version is not null 
and s.startCoordinate is not null 
and s.endCoordinate is not null 
and s.variantSequence is not null 
and s.referenceSequence is not null
''', None)

db.sql('create index idx1 on noDescription(_Allele_key)', None)

results = db.sql('''
select 
a.accID as alleleID, 
aa.symbol, 
m.chromosome, 
n.startCoordinate, 
n.endCoordinate, 
n.referencesequence, 
n.variantSequence 
from noDescription n, MRK_Marker m, ALL_Allele aa, ACC_Accession a 
where n._Allele_key = aa._Allele_key 
and aa._Marker_key = m._Marker_key 
and n._Allele_key = a._Object_key 
and a._MGIType_key = 11 
and a._LogicalDB_key = 1 
and a.preferred = 1 
and a.prefixPart = 'MGI:'
order by aa.symbol
''', 'auto')

sys.stdout.write('alleleID' + TAB)
sys.stdout.write('symbol' + TAB)
sys.stdout.write('chromosome' + TAB)
sys.stdout.write('startCoordinate' + TAB)
sys.stdout.write('endCoordinate' + TAB)
sys.stdout.write('referencesequence' + TAB)
sys.stdout.write('variantSequence' + CRT)

for r in results:
        sys.stdout.write(r['alleleID'] + TAB)
        sys.stdout.write(r['symbol'] + TAB)
        sys.stdout.write(r['chromosome'] + TAB)
        sys.stdout.write(str(r['startCoordinate']) + TAB)
        sys.stdout.write(str(r['endCoordinate']) + TAB)
        sys.stdout.write(r['referencesequence'] + TAB)
        sys.stdout.write(r['variantSequence'] + CRT)

sys.stdout.flush()

