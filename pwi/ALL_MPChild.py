
'''
#
# MP Term and Child Annotations
#
# Retrieve all annotated genotypes, and any notes for the specified MP Term ID, or any of its children. Ordered by allelepairs, genotype_id, annotatedTerm, jnum, _note_key
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
select 
accg.accid genotype_id, 
mng.note as allelepairs, 
strain.strain as geneticBackground, 
accr.accid as jnum_id, 
t.term as annotatedTerm, 
acc_term.accid as annotatedTermId, 
mn._note_key, 
nt.notetype as type, 
mn.note 
from voc_annot annot 
        join voc_evidence ev on (ev._annot_key = annot._annot_key) 
        join acc_accession accg on 
                (accg._object_key = annot._object_key 
                 and accg._mgitype_key = 12 
                 and accg.preferred = 1 
                 and accg._logicaldb_key = 1 
                 and accg.prefixpart = 'MGI:') 
        join gxd_genotype g on (g._genotype_key = annot._object_key) 
        join prb_strain strain on (strain._strain_key = g._strain_key) 
        join mgi_note mng on (mng._object_key = annot._object_key and mng._mgitype_key = 12 and mng._notetype_key = 1016) 
        join voc_term t on (t._term_key = annot._term_key) 
        join acc_accession acc_term on (acc_term._object_key = t._term_key and acc_term.preferred = 1 and acc_term._mgitype_key = 13) 
        join acc_accession accr on (accr._object_key = ev._refs_key and accr._mgitype_key = 1 and accr.preferred = 1 and accr.prefixpart = 'J:') 
                left outer join mgi_note mn on (mn._object_key = ev._annotevidence_key and mn._mgitype_key = 25) 
                left outer join mgi_notetype nt on (nt._notetype_key = mn._notetype_key) 
where annot._annottype_key = 1002 

and (

acc_term.accid = '%s' 

OR exists (select 1 from acc_accession a, dag_closure dc
    where a.accid = '%s' 
    and a._mgitype_key = 13 
    and a._object_key = dc._ancestorobject_key 
    and dc._mgitype_key = 13
    and dc._descendentobject_key = annot._term_key
    )
) 
order by allelepairs, genotype_id, annotatedTerm, jnum_id, mn._note_key 
''' % (value, value), 'auto')

sys.stdout.write('genotype_id' + TAB)
sys.stdout.write('allelepairs' + TAB)
sys.stdout.write('geneticBackground' + TAB)
sys.stdout.write('jnum_id' + TAB)
sys.stdout.write('annotatedTerm' + TAB)
sys.stdout.write('annotatedTermId' + TAB)
sys.stdout.write('_note_key' + TAB)
sys.stdout.write('type' + TAB)
sys.stdout.write('note' + CRT)

for r in results:
        sys.stdout.write(r['genotype_id'] + TAB)
        sys.stdout.write(r['allelepairs'].replace('\n', ' ') + TAB)
        sys.stdout.write(r['geneticBackground'] + TAB)
        sys.stdout.write(r['jnum_id'] + TAB)
        sys.stdout.write(r['annotatedTerm'] + TAB)
        sys.stdout.write(r['annotatedTermId'] + TAB)

        if r['note'] == None:
                sys.stdout.write(3*TAB + CRT)
        else:
                sys.stdout.write(str(r['_note_key']) + TAB)
                sys.stdout.write(r['type'] + TAB)
                sys.stdout.write(r['note'] + CRT)

sys.stdout.flush()

