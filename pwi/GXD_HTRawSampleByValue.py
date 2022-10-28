
'''
#
# GXD HT Raw Sample Value Search
#
# Search GXD HT Raw Sample Value 
# -- sort by relevance, experiment ID, sample ID 
# -- results limited to 5000 
# -- both key and value columns are aggregated
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
select a.accid as ExperimentID, 
t2.term as experimenttype, 
rs.accid as SampleID, 
t.term as relevance, 
string_agg(distinct kv.key, ', ') as keys, 
string_agg(distinct kv.value, ', ') as values 
from gxd_htrawsample rs, 
     mgi_keyvalue kv, 
     gxd_htexperiment e, 
     voc_term t, 
     voc_term t2, 
     acc_accession a 
where kv.value ilike '%s' 
and kv._mgitype_key = 47 -- raw sample 
and kv._object_key = rs._rawsample_key 
and rs._experiment_key = e._experiment_key 
and e._evaluationstate_key = t._term_key 
and e._experimenttype_key = t2._term_key 
and e._experiment_key = a._object_key 
and a._mgitype_key = 42 -- experiment 
and a._logicaldb_key = 190 
and a.preferred = 1 
group by 1, 2, 3, 4 
order by t.term desc, a.accid, rs.accid 
limit 5000
''' % (value), 'auto')

for r in results:
        sys.stdout.write(r['ExperimentID'] + TAB)
        sys.stdout.write(r['experimenttype'] + TAB)
        sys.stdout.write(r['SampleID'] + TAB)
        sys.stdout.write(r['relevance'] + TAB)
        sys.stdout.write(r['keys'] + TAB)
        sys.stdout.write(r['values'] + CRT)

sys.stdout.flush()

