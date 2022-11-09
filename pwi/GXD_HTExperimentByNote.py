
'''
#
# GXD HT Experiment Note Search
#
# This report would display searches of the Experiment Note field. 
# Although I can search this field in the pwi module, it would be helpful to get the results as a report 
# (rather than having to toggle through them). 
#
# Report name: GXD HT Experiment Note Search 
# Sort: 
#       Primary: Experiment Type 
#       Secondary: Evaluation State 
#       Tertiary: Experiment ID
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

value = sys.argv[1]

results = db.sql('''
select a.accid as ExperimentID, 
t2.term as experimenttype, 
t.term as relevance, 
n.note 
from gxd_htexperiment e, voc_term t, voc_term t2, acc_accession a, mgi_note n 
where e._evaluationstate_key = t._term_key 
and e._experimenttype_key = t2._term_key 
and e._experiment_key = a._object_key 
and a._mgitype_key = 42 
and a._logicaldb_key in (189,190) 
and a.preferred = 1 
and e._experiment_key = n._object_key 
and n._notetype_key = 1047 
and lower(n.note) like lower('%s') 
group by 1, 2, 3, 4 
order by t2.term, t.term, a.accid
''' % (value), 'auto')

sys.stdout.write('ExperimentID' + TAB)
sys.stdout.write('experimenttype' + TAB)
sys.stdout.write('relevance' + TAB)
sys.stdout.write('note' + CRT)

for r in results:
        sys.stdout.write(r['ExperimentID'] + TAB)
        sys.stdout.write(r['experimenttype'] + TAB)
        sys.stdout.write(r['relevance'] + TAB)
        sys.stdout.write(r['note'] + CRT)

sys.stdout.flush()

