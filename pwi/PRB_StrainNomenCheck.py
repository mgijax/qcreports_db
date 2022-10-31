
'''
#
# Strain Check by Strain Nomenclature
#
# Lookup IMSR Strain Info by Strain Nomenclature 
#
# Enter a space delimited set of strain names 
#
# Examples: MRL/MpJ 129.B6-GIX<->/Rbrc
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

# expects "MRL/MpJ 129.B6-GIX<->/Rbrc"
value = list(sys.argv[1].split(' '))

# example: 'MRL/MpJ','129.B6-GIX<->/Rbrc'
value1 = "'" + "','".join(value) + "'"

db.sql('''
select 
s.strain, 
s._strain_key, 
ms.synonym 
into temporary table strainSynHist 
from mgi_synonym ms, prb_strain s 
where ms._synonymtype_key in (1000, 1001) 
and s.strain in (%s) 
and s._strain_key = ms._object_key 
order by s.strain
''' % (value1), None)
db.sql('create index idx1 on strainSynHist(_strain_key)', None)

db.sql('''
select 
s.strain, 
s._strain_key, 
a1.accid as mgiID, 
CASE WHEN s.private = 0 THEN 'No' ELSE 'Yes' END AS private 
into temporary table strains 
from prb_strain s, acc_accession a1 
where strain in (%s) 
and s._strain_key = a1._object_key 
and a1._MGIType_key = 10 
and a1._LogicalDB_key = 1 
and a1.prefixPart = 'MGI:' 
and a1.preferred = 1
''' % (value1), None)
db.sql('create index idx2 on strains(_strain_key)', None)

db.sql('''
select s.*, a.accid as repoID 
into temporary table repoIDs 
from strains s left outer join acc_accession a on (s._strain_key = a._object_key and a._mgitype_key = 10 and a._logicaldb_key not in (1) and a.preferred = 1)
''', None)
db.sql('create index idx3 on repoIDs(_strain_key)', None)

db.sql('''
select s.strain, 
s._strain_key, 
s.mgiID, 
s.private, 
string_agg(distinct s.repoID, ', ') as repoIDS, 
string_agg(distinct a.symbol, ', ') as alleleSymbols 
into temporary table final 
from repoIDs s left outer join all_allele a on (s._strain_key = a._strain_key and a._allele_status_key in (847114, 3983021)) 
group by 1, 2, 3, 4 order by s.strain
''', None)
db.sql('create index idx4 on final(_strain_key)', None)

results = db.sql('''
select f.strain, 
CASE WHEN sh.synonym is null THEN 'No' ELSE 'Yes' END AS synonymOrHistory, 
f.mgiID, 
f.private, 
f.repoids, 
f.alleleSymbols 
from final f left outer join strainSynHist sh on (f._strain_key = sh._strain_key) 
order by f.strain
''', 'auto')

sys.stdout.write('strain' + TAB)
sys.stdout.write('synonymOrHistory' + TAB)
sys.stdout.write('mgiID' + TAB)
sys.stdout.write('private' + TAB)
sys.stdout.write('repoids' + TAB)
sys.stdout.write('alleleSymbols' + CRT)

for r in results:
        sys.stdout.write(r['strain'] + TAB)
        sys.stdout.write(r['synonymOrHistory'] + TAB)
        sys.stdout.write(r['mgiID'] + TAB)
        sys.stdout.write(r['private'] + TAB)
        sys.stdout.write(r['repoids'] + TAB)

        if r['alleleSymbols'] == None:
                sys.stdout.write(CRT)
        else:
                sys.stdout.write(r['alleleSymbols'] + CRT)

sys.stdout.flush()

