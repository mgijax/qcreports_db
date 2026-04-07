'''
#
# TR11942
#
# Report:
#
# Report any MGI id used in assay or specimen notes that is invalid.
# Fields for specimen notes report:
# J#
# Assay ID
# Gene
# Assay Type
# Specimen Label
# Age
# Specimen Note
#
# Sort by J# then assay id
#
'''

import sys 
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Invalid MGI ids used in assay and specimen notes', os.environ['QCOUTPUTDIR'])

cmd = '''
select c.jnumid, c.numericpart, a.accid, m.symbol, gt.assaytype, gs.specimenlabel, gs.age, gs.specimennote as note
from gxd_assay ga, bib_citation_cache c, acc_accession a, mrk_marker m, gxd_assaytype gt, gxd_specimen gs
where ga._refs_key = c._refs_key
and ga._assay_key = a._object_key
and a._mgitype_key = 8
and ga._marker_key = m._marker_key
and ga._assaytype_key = gt._assaytype_key
and ga._assay_key = gs._assay_key
and gs.specimennote like '%MGI:%'
order by c.numericpart, a.accid
'''

results = db.sql(cmd, 'auto')

for r in results:
    notes = r['note'].split('MGI:')
    notes = notes[1].split('|')
    notes = notes[0].split('(')
    notes = notes[0].split(')')
    notes = notes[0].split('.')
    accid = 'MGI:' + notes[0]
    accid = accid.replace(' ', '')
    findmgiid = db.sql('''select * from acc_accession where accid = '%s' ''' % (accid), 'auto')
    if len(findmgiid) == 0:
        #print('''select * from acc_accession where accid = '%s' ''' % (accid))
        fp.write(r['jnumid'] + TAB)
        fp.write(r['accid'] + TAB)
        fp.write(r['symbol'] + TAB)
        fp.write(r['assaytype'] + TAB)
        fp.write(r['specimenlabel'] + TAB)
        fp.write(r['age'] + TAB)
        fp.write(r['note'] + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

