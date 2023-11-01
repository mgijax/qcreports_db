
'''
#
# GXD HT Raw Sample Value Search 2
#
# Search GXD HT Raw Sample Value 
# -- sort by experment type, relevance, experiment id
# -- results limited to 5000 
# -- both key and value columns are aggregated
#
# 1: Experiment ID (tertiary sort)
# 2: Experiment Type (primary sort)
# 3: Relevance (secondary sort using the same custom ordering we use for the GXD HT Raw Sample Value Search).
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
select distinct a.accid as ExperimentID, 
t2.term as experimenttype, 
t.term as relevance,
e.name
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
order by t2.term, t.term, a.accid 
limit 5000
''' % (value), 'auto')

sys.stdout.write('ExperimentID' + TAB)
sys.stdout.write('experimenttype' + TAB)
sys.stdout.write('relevance' + TAB)
sys.stdout.write('title' + CRT)

for r in results:
        sys.stdout.write(r['ExperimentID'] + TAB)
        sys.stdout.write(r['experimenttype'] + TAB)
        sys.stdout.write(r['relevance'] + TAB)
        sys.stdout.write(r['name'] + CRT)

sys.stdout.flush()

