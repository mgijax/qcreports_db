
'''
#
# GXD Result Note Search
#
# Searches InSitu Result Notes by note text (via contains search). 
# Search is restricted to Immunohistochemistry, In situ reporter (knock-in) and RNA in situ assays. 
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

value = sys.argv[1]

results = db.sql('''
select distinct ac.accid as assay_mgiid, 
ac_ref.accid as jnum_id, 
gs.specimenlabel, 
m.symbol as gene, 
gisrs._stage_key as stage, 
s.term as structure, 
c.term as celltype, 
gisr.resultnote 
from GXD_Specimen gs 
        join GXD_Assay ga on ga._assay_key = gs._assay_key 
        join ACC_Accession ac on ac._object_key = ga._assay_key and ac.preferred = 1 and ac._mgitype_key = 8 and ac._logicaldb_key = 1 
        join ACC_Accession ac_ref on ac_ref._object_key = ga._refs_key 
                and ac_ref.preferred = 1 
                and ac_ref._mgitype_key = 1 
                and ac_ref.prefixpart = 'J:' 
                and ac_ref._logicaldb_key = 1 
        join MRK_Marker m on m._marker_key = ga._marker_key 
        join GXD_InSituResult gisr on gisr._specimen_key = gs._specimen_key 
        join GXD_ISResultStructure gisrs on gisrs._result_key = gisr._result_key 
        join VOC_Term s on gisrs._emapa_term_key = s._term_key 
        left join GXD_ISResultCellType giscell on giscell._result_key = gisr._result_key 
        left join VOC_Term c on giscell._celltype_term_key = c._term_key 
where ga._AssayType_key in (1, 6, 9) 
and lower(gisr.resultNote) like lower('%s') 
order by gisrs._stage_key, s.term
''' % (value), 'auto')

sys.stdout.write('assay_mgiid' + TAB)
sys.stdout.write('jnum_id' + TAB)
sys.stdout.write('specimenlabel' + TAB)
sys.stdout.write('gene' + TAB)
sys.stdout.write('stage' + TAB)
sys.stdout.write('structure' + TAB)
sys.stdout.write('celltype' + TAB)
sys.stdout.write('resultnote' + CRT)

for r in results:
        sys.stdout.write(r['assay_mgiid'] + TAB)
        sys.stdout.write(r['jnum_id'] + TAB)

        if r['specimenlabel'] == None:
                sys.stdout.write(TAB)
        else:
                sys.stdout.write(r['specimenlabel'] + TAB)

        sys.stdout.write(r['gene'] + TAB)
        sys.stdout.write(str(r['stage']) + TAB)
        sys.stdout.write(r['structure'] + TAB)

        if r['celltype'] == None:
                sys.stdout.write(TAB)
        else:
                sys.stdout.write(r['celltype'] + TAB)

        sys.stdout.write(r['resultnote'] + CRT)

sys.stdout.flush()

