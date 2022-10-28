
'''
#
# GXD HT Sample Note Search
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

value = '%' + sys.argv[1] + '%'

results = db.sql('''
select a1.accid as expID, 
hts.name as sampleName, 
t2.term as relevance, 
hts.age as sampleAge, 
t.term as emapaTerm, 
ts.stage, 
t3.term as cellTypeTerm, 
n.note as sampleNote 
from MGI_Note n, 
     GXD_HTSample hts left join VOC_Term t3 on hts._CellType_Term_key = t3._Term_key , 
     VOC_Term t, 
     ACC_Accession a1, 
     VOC_Term t2, 
     GXD_TheilerStage ts 
where n._Notetype_key = 1048 
and lower(n.note) like lower('%s') 
and n._Object_key = hts._Sample_key 
and hts._emapa_key = t._Term_key 
and hts._Experiment_key = a1._Object_key 
and a1._MGIType_key = 42 
and a1.preferred = 1 
and a1._LogicalDB_key in (189,190) 
and hts._Relevance_key = t2._Term_key 
and hts._Stage_key = ts._Stage_key      
''' % (value), 'auto')

for r in results:
        sys.stdout.write(r['expID'] + TAB)
        sys.stdout.write(r['sampleName'] + TAB)
        sys.stdout.write(r['relevance'] + TAB)
        sys.stdout.write(r['sampleAge'] + TAB)
        sys.stdout.write(r['emapaTerm'] + TAB)
        sys.stdout.write(str(r['stage']) + TAB)

        if r['cellTypeTerm'] == None:
                sys.stdout.write(TAB)
        else:
                sys.stdout.write(r['cellTypeTerm'] + TAB)

        sys.stdout.write(r['sampleNote'] + CRT)

sys.stdout.flush()

