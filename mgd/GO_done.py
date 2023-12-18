
'''
#
# GO_done.py
#
# Report:
#       
# A report of all markers with GO Annotations 
# where the GO Annotation has a completion date.
#
# field 1: Gene Symbol
# field 2: Gene Accession ID
# field 3: Completion Date
# field 4: # of outstanding references
# field 5: list of references that have not yet been annotated to the gene
#	   whose creation date is greater than the completion date.
# exclude J:60000,J:73065,J:72245,J:80000,J:72247,J:99680
#
# Usage:
#       GO_done.py
#
# History:
#
# 04/26/2021	lec
#       - wts2-526/adjustment needed to "complete' in GO EI (TR13354)
#       adjustment also needed to remove "isReferenceGene" (obsolete)
#
# 01/28/2010	lec
#	- TR9612/select jnumbers into list
#
# 01/06/2010	lec
#	- TR9996/modification to "more than 5 references"
#
# 10/24/2006	lec
#	- TR7533/7920; GO tracking
#
# 10/17/2006	lec
#	- TR 7976; added Reference genes; more columns
#
# 08/28/2006	lec
#	- TR 7876; added headings and Refs_used column
#
# 03/02/2006	lec
#	- TR 7532
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], fileExt = '.mgi', outputdir = os.environ['QCOUTPUTDIR'])
fp.write(CRT)
fp.write('# field 1: Gene Symbol' + CRT)
fp.write('# field 2: MGI-ID' + CRT)
fp.write('# field 3: Date_complete' + CRT)
fp.write('# field 4: outstanding_refs' + CRT)
fp.write('# field 5: list of references that have not yet been annotated to the gene' + CRT)
fp.write('#	   whose creation date is greater than the completion date' + CRT*2)
fp.write('# exclude J:60000,J:73065,J:72245,J:80000,J:72247,J:99680' + CRT*2)

#
# select all Markers w/ GO Annotations that contains a completion date
# exclude 3 red 
#
db.sql('''
        select t.completion_date as cdate, 
               m._Marker_key, m.symbol, a.accID 
        into temporary table godone 
        from GO_Tracking t, MRK_Marker m, ACC_Accession a 
        where t.completion_date is not null 
        and t._Marker_key = m._Marker_key 
        and m._Marker_Status_key in (1,3)
        and m._Marker_key = a._Object_key 
        and a._MGIType_key = 2 
        and a._LogicalDB_key = 1 
        and a.prefixPart = 'MGI:' 
        and a.preferred = 1 
        and exists (select 1 from VOC_Annot v where t._Marker_key = v._Object_key and v._AnnotType_key = 1000)
        and not exists (select 1 from VOC_Annot v where t._Marker_key = v._Object_key and v._AnnotType_key = 1000 and v._Term_key = 120)
        and not exists (select 1 from VOC_Annot v where t._Marker_key = v._Object_key and v._AnnotType_key = 1000 and v._Term_key = 1098)
        and not exists (select 1 from VOC_Annot v where t._Marker_key = v._Object_key and v._AnnotType_key = 1000 and v._Term_key = 6113)
        ''', None)
db.sql('create index godone_idx1 on godone(_Marker_key)', None)

# exclude J:60000,J:73065,J:72245,J:80000,J:72247,J:99680
results = db.sql('''
        select b._Marker_key, b.jnumID 
        from BIB_GOXRef_View b, godone g
        where b._Marker_key = g._Marker_key
        and b.creation_date > (g.cdate + interval '1 day')
        and b._Refs_key not in (61933,73197,73199,74017,80961,100707)
        and not exists (select 1 from VOC_Annot a, VOC_Evidence e 
                where a._AnnotType_key = 1000 
                and a._Annot_key = e._Annot_key 
                and e._Refs_key = b._Refs_key) 
        ''', 'auto')

jnums = {}
for r in results: 
    key = r['_Marker_key']
    value = r['jnumID']
    if key not in jnums:
        jnums[key] = []
    jnums[key].append(r['jnumID'])

counter = 0
results = db.sql('select * from godone order by symbol', 'auto')
for r in results:

    key = r['_Marker_key']

    if key not in jnums:
        continue

    fp.write(r['symbol'] + TAB)
    fp.write(r['accID'] + TAB)
    fp.write(str(r['cdate']) + TAB)

    if key in jnums:
        fp.write(str(len(jnums[key])) + TAB + ','.join(jnums[key]) + CRT)
    else:
        fp.write('0' + TAB + CRT)

    counter += 1

fp.write(CRT * 2)
fp.write('total number of completed genes: %s\n' % (str(counter)))
reportlib.finish_nonps(fp)
