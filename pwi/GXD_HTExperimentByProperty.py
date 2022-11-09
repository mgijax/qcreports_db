
'''
#
# GXD HT Experiment Properties Search
#
# -- Raw Experimental Factor 
# -- Raw Experiment Type 
# -- Raw Contact Name (Provider) 
# -- PubMed ID
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
select a1.accid as expID, 
hte.name as title, 
t2.term as evaluationState, 
t3.term as curationState, 
t1.term as propertyName, 
p.value as propertyValue 
from MGI_Property p, 
     GXD_HTExperiment hte, 
     VOC_Term t1, 
     VOC_Term t2, 
     VOC_Term t3, 
     ACC_Accession a1 
where p._PropertyType_key = 1002 
and lower(p.value) like lower('%s') 
and p._PropertyTerm_key = t1._Term_key 
and t1._Term_key in (20475423, 20475425, 20475426, 20475430) --factor, type, name, pubmedID 
and p._Object_key = hte._Experiment_key 
and hte._Experiment_key = a1._Object_key 
and a1._MGIType_key = 42 
and a1.preferred = 1 
and a1._LogicalDB_key in (189,190) --arrayExp, geo 
and hte._evaluationstate_key = t2._term_key 
and hte._curationstate_key = t3._term_key 
order by t3.term, t2.term, a1.accid
''' % (value), 'auto')

sys.stdout.write('expID' + TAB)
sys.stdout.write('title' + TAB)
sys.stdout.write('evaluationState' + TAB)
sys.stdout.write('curationState' + TAB)
sys.stdout.write('propertyName' + TAB)
sys.stdout.write('propertyValue' + CRT)

for r in results:
        sys.stdout.write(r['expID'] + TAB)
        sys.stdout.write(r['title'] + TAB)
        sys.stdout.write(r['evaluationState'] + TAB)
        sys.stdout.write(r['curationState'] + TAB)
        sys.stdout.write(r['propertyName'] + TAB)
        sys.stdout.write(r['propertyValue'] + CRT)

sys.stdout.flush()

