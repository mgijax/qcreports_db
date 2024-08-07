
'''
#
# GXD HT Raw Sample Key Search
#
# Search GXD HT Raw Sample Key 
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

def go (form) :
    value = '%' + form['arg'].value + '%'

    results = db.sql('''
    select a.accid as ExperimentID, 
    t2.term as experimenttype, 
    rs.accid as SampleID, 
    t.term as relevance, 
    string_agg(distinct kv.key, ', ') as keys, 
    string_agg(distinct kv.value, ', ') as values,
    case 
            when t.term = 'Predicted Yes' then 1 
            when t.term = 'Predicted No' then 2 
            when t.term = 'Maybe' then 3 
            when t.term = 'Yes' then 4 
            when t.term = 'No' then 5
    end as relevanceOrder
    from gxd_htrawsample rs, 
         mgi_keyvalue kv, 
         gxd_htexperiment e, 
         voc_term t, 
         voc_term t2, 
         acc_accession a 
    where kv.key ilike '%s' 
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
    order by relevanceOrder, a.accid, rs.accid 
    limit 5000
    ''' % (value), 'auto')

    sys.stdout.write('ExperimentID' + TAB)
    sys.stdout.write('experimenttype' + TAB)
    sys.stdout.write('SampleID' + TAB)
    sys.stdout.write('relevance' + TAB)
    sys.stdout.write('keys' + TAB)
    sys.stdout.write('values' + CRT)

    for r in results:
            sys.stdout.write(r['ExperimentID'] + TAB)
            sys.stdout.write(r['experimenttype'] + TAB)
            sys.stdout.write(r['SampleID'] + TAB)
            sys.stdout.write(r['relevance'] + TAB)
            sys.stdout.write(r['keys'] + TAB)
            sys.stdout.write(r['values'] + CRT)

    sys.stdout.flush()

