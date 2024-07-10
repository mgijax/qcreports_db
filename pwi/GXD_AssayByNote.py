
'''
#
# GXD Assay Note Search
#
# Searches Assay note text (via contains search). 
# Search excludes In situ reporter (knock in), In situ reporter (transgenic), Recombinase reporter
# Case insensitive. 
# "%" is wildcard for multiple characters. 
# "?" is wildcard for a single character. 
# Spaces, alphanumerics, and most "punctuation" characters (except wildcards) are recognized literally as searchable characters. 
# Words are AND'ed together. 
# Word order is enforced. 
# Uses a Contains search on each word, so "respond to" also will return "correspond to". 
# Some results are a little unpredictable because browsers will suppress extra spaces in the display that do exist in the data, 
#       for example, search for "section. In" (no quotes, two spaces after the period) and compare to display.
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
    select distinct 
    ac_ref.accid as jnum_id, 
    ac.accid as assay_mgiid, 
    m.symbol as gene, 
    gat.assaytype,
    n.assaynote
    from GXD_Assay ga, GXD_AssayNote n, ACC_Accession ac, ACC_Accession ac_ref, MRK_Marker m, GXD_AssayType gat
    where ga._assaytype_key not in (10,11)
    and ga._assaytype_key = gat._assaytype_key
    and lower(n.assaynote) like lower('%s') 
    and ga._assay_key = n._assay_key 
    and ac._object_key = ga._assay_key and ac.preferred = 1 and ac._mgitype_key = 8 and ac._logicaldb_key = 1 
    and ac_ref._object_key = ga._refs_key 
    and ac_ref.preferred = 1 
    and ac_ref._mgitype_key = 1 
    and ac_ref.prefixpart = 'J:' 
    and ac_ref._logicaldb_key = 1 
    and m._marker_key = ga._marker_key 
    order by jnum_id, assay_mgiid
    ''' % (value), 'auto')

    sys.stdout.write('jnum_id' + TAB)
    sys.stdout.write('assay_mgiid' + TAB)
    sys.stdout.write('gene' + TAB)
    sys.stdout.write('assay type' + TAB)
    sys.stdout.write('assaynote' + CRT)

    for r in results:
            sys.stdout.write(r['jnum_id'] + TAB)
            sys.stdout.write(r['assay_mgiid'] + TAB)
            sys.stdout.write(r['gene'] + TAB)
            sys.stdout.write(r['assaytype'] + TAB)
            note = r['assaynote'].replace('\n', ' ').replace('\t', ' ')
            sys.stdout.write(note + CRT)

    sys.stdout.flush()

