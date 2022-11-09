
'''
#
# GXD HT Sample Name Search
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
select a1.accid as expID, hts.name as title 
from GXD_HTSample hts, ACC_Accession a1 
where lower(hts.name) like lower('%s') 
and hts._Experiment_key = a1._Object_key 
and a1._MGIType_key = 42 
and a1.preferred = 1 
and a1._LogicalDB_key in (189,190) --arrayExp, geo order by a1.accid
''' % (value), 'auto')

sys.stdout.write('expID' + TAB)
sys.stdout.write('title' + CRT)

for r in results:
        sys.stdout.write(r['expID'] + TAB)
        sys.stdout.write(r['title'] + CRT)

sys.stdout.flush()

