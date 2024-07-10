
'''
#
# MP Term Genotype and Notes QC
#
# Retrieve all directly annotated genotypes, and any notes for the specified MP Term ID. Requested in TR10423.
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
    value = form['arg'].value

    results = db.sql('''
    select 
    accg.accid genotype_id, 
    accr.accid jnum_id, 
    mn._note_key, 
    nt.notetype, 
    mn.note 
    from voc_annot annot 
            join voc_evidence ev on (ev._annot_key = annot._annot_key) 
            join acc_accession acct on (acct._object_key = annot._term_key and acct._mgitype_key = 13) 
            join acc_accession accg on (accg._object_key = annot._object_key 
                    and accg._mgitype_key = 12 
                    and accg.preferred = 1 
                    and accg._logicaldb_key = 1 
                    and accg.prefixpart = 'MGI:') 
            join acc_accession accr on (accr._object_key = ev._refs_key 
                    and accr._mgitype_key = 1 
                    and accr.preferred = 1 
                    and accr.prefixpart = 'J:' ) 
                    left outer join mgi_note mn on (mn._object_key = ev._annotevidence_key and mn._mgitype_key = 25) 
                    left outer join mgi_notetype nt on (nt._notetype_key = mn._notetype_key) 
    where annot._AnnotType_key = 1002 
    and acct.accid = '%s' 
    order by genotype_id, jnum_id, mn._note_key
    ''' % (value), 'auto')

    sys.stdout.write('genotype_id' + TAB)
    sys.stdout.write('jnum_id' + TAB)
    sys.stdout.write('_note_key' + TAB)
    sys.stdout.write('notetype' + TAB)
    sys.stdout.write('note' + CRT)

    for r in results:
            sys.stdout.write(r['genotype_id'] + TAB)
            sys.stdout.write(r['jnum_id'] + TAB)

            if r['note'] == None:
                    sys.stdout.write(3*TAB + CRT)
            else:
                    note = r['note'].replace('\n', ' ').replace('\t', ' ')
                    sys.stdout.write(str(r['_note_key']) + TAB)
                    sys.stdout.write(r['notetype'] + TAB)
                    sys.stdout.write(note + CRT)

    sys.stdout.flush()

