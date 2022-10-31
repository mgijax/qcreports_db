
'''
#
# Vairants to be reviewed
#
# Report variants where: 
#       all five curated genomic fields are not null
#       reviewed box is not checked 
#
#       Columns: 
#               Allele ID 
#               Allele Symbol 
#               Curator Notes
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
select v._Allele_key 
into temporary table notReviewed 
from ALL_Variant v, ALL_Variant_Sequence s 
where v._sourcevariant_key is not null 
and v.isreviewed = 0 
and v._Variant_key = s._Variant_key 
and s._Sequence_type_key = 316347 --dna 
and s.version is not null 
and s.startCoordinate is not null 
and s.endCoordinate is not null 
and s.variantSequence is not null 
and s.referenceSequence is not null
''', None)

db.sql('create index idx1 on notReviewed(_Allele_key)', None)

db.sql('''
select mn._Object_key, mn.note 
into temporary table curNote 
from MGI_Note mn 
where mn._Notetype_key = 1050
''', None)

db.sql('create index idx2 on curNote(_Object_key)', None)

results = db.sql('''
select distinct a.accID as alleleID, 
aa.symbol as alleleSymbol, 
nn.note as curatorNote 
from ACC_Accession a, 
ALL_Allele aa, 
notReviewed n left outer join curNote nn on n._Allele_key = nn._Object_key 
where n._Allele_key = aa._Allele_key 
and n._Allele_key = a._Object_key 
and a._MGIType_key = 11 
and a._LogicalDB_key = 1 
and a.preferred = 1 
and a.prefixPart = 'MGI:' 
order by aa.symbol
''', 'auto')

for r in results:
        sys.stdout.write(r['alleleID'] + TAB)
        sys.stdout.write(r['alleleSymbol'] + TAB)

        if r['curatorNote'] == None:
                sys.stdout.write(CRT)
        else:
                sys.stdout.write(r['curatorNote'] + CRT)

sys.stdout.flush()

