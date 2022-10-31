
'''
#
# Variants to be curated
#
# Report variants where: 
#       the allele has source variant data
#       has no curated variant data 
#
# Columns: 
#       Allele ID 
#       Allele Symbol
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

# This gets curated variants that have null descriptions 
db.sql('''
select _variant_key as c_variant_key, _allele_key, _sourcevariant_key as s_variant_key, description 
INTO TEMP temp1 
from all_variant 
where _sourcevariant_key is not null 
and description is null
''', None)

db.sql('CREATE INDEX idx1 ON temp1 (c_variant_key)', None)

# This gets curated variants from temp1 with no variant sequence records 
db.sql('''
select t1.c_variant_key, t1._allele_key, t1.s_variant_key, t1.description 
INTO TEMP temp2 
from temp1 t1 LEFT OUTER JOIN all_variant_sequence avs on (t1.c_variant_key = avs._variant_key) 
where avs._variant_key is null
''', None)

db.sql('CREATE INDEX idx2 ON temp2 (_allele_key)', None)

# This just gets the allele MGI IDs and symbols 
results = db.sql('''
select a.accid, al.symbol 
from temp2 t2, all_allele al, acc_accession a 
where a._logicaldb_key = 1 
and a.prefixpart = 'MGI:' 
and a.preferred = 1 
and a._mgitype_key = 11 
and a._object_key = t2._allele_key 
and al._allele_key = t2._allele_key order by al.symbol
''', 'auto')

for r in results:
        sys.stdout.write(r['accid'] + TAB)
        sys.stdout.write(r['symbol'] + CRT)

sys.stdout.flush()

