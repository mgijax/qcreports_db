
'''
#
# Allele Check by Creation Date
#
# Look up allele information based on data of creation.
#
'''
 
import sys
import os
import db
import reportlib

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

value = sys.argv[1]

results = db.sql('''
select aa.accid as mgi_id, a.symbol, u.login as created_by, n.note
from ALL_Allele a
        left outer join MGI_Note n on (n._object_key = a._allele_key and n._mgitype_key = 8 and n._notetype_key = 1022)
        ,
ACC_Accession aa, MGI_User u
where a._allele_key = aa._object_key
and aa._mgitype_key = 11
and a._createdby_key = u._user_key
and (a.creation_date between '%s' and ('%s'::date + '1 day'::interval))
order by a.symbol
''' % (value, value), 'auto')

sys.stdout.write('symbol' + TAB)
sys.stdout.write('mgi_id' + TAB)
sys.stdout.write('note' + TAB)
sys.stdout.write('created_by' + CRT)

for r in results:
        sys.stdout.write(r['symbol'] + TAB)
        sys.stdout.write(r['mgi_id'] + TAB)

        if r['note'] == None:
                sys.stdout.write(3*TAB + TAB)
        else:
                note = r['note'].replace('\n', ' ').replace('\t', ' ')
                sys.stdout.write(note + TAB)

        sys.stdout.write(r['created_by'] + CRT)

sys.stdout.flush()

