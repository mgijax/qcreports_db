'''
#
# Purpose:
#       Unannotated genes
#
# History
#       lec     02/22/2023
#       fl2-210/Request for additional GO QC report: under-annotated genes (TR13434)
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Unannotated genes', os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('mgi_id' + TAB)
fp.write('symbol' + TAB)
fp.write('marker_type' + TAB)
fp.write('feature_type' + TAB)
fp.write('completion_date' + TAB)
fp.write('EXP_annotations' + TAB)
fp.write('ISO_annotations' + TAB)
fp.write('used_refs' + TAB)
fp.write('outstanding_refs' + TAB)
fp.write('ratio' + TAB)
fp.write('after_completion' + TAB)
fp.write('GXD_refs' + TAB)
fp.write('non_GXD_refs' + TAB)
fp.write('DO_annotations' + TAB)
fp.write('curator_to_review' + CRT)

# all GO annotated markers
db.sql('''
select m._marker_key, m.symbol, mcv.term as featureType, a.accID as mgiID, mt.name as markerType, gt.completion_date
into temp table gomarkers
from MRK_Marker m, MRK_MCV_Cache mcv, ACC_Accession a, MRK_Types mt, GO_Tracking gt
where m._marker_key = mcv._marker_key
and mcv.qualifier = 'D'
and m._marker_key = a._object_key
and a._mgitype_key = 2
and a._logicaldb_key = 1
and a.preferred = 1
and m._marker_type_key = mt._marker_type_key
and m._marker_key = gt._marker_key
and exists (select 1 from VOC_Annot v where v._annottype_key = 1000 and v._object_key = m._marker_key)
''', None)

db.sql('create index idx1 on gomarkers(_marker_key)', None)

#
# exp_annotations : >1 and <21
#
results = db.sql('''
select m._marker_key, count(ve._annotevidence_key) as counter
from gomarkers m, VOC_Annot v, VOC_Evidence ve, VOC_Term t, BIB_Citation_Cache c
where m._marker_key = v._object_key
and v._annottype_key = 1000
and v._annot_key = ve._annot_key
and ve._evidenceterm_key = t._term_key
and t.abbreviation in ('EXP','IDA','IPI','IMP','IGI','IEP')
and ve._refs_key = c._refs_key
and c.pubmedid is not null
group by _marker_key having count(*) between 2 and 20
''', 'auto')
exp_annotations = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in exp_annotations:
                exp_annotations[key] = []
        exp_annotations[key].append(value)
#print(exp_annotations)

#
# iso_annotations
#
results = db.sql('''
select m._marker_key, count(ve._annotevidence_key) as counter
from gomarkers m, VOC_Annot v, VOC_Evidence ve, VOC_Term t
where m._marker_key = v._object_key
and v._annottype_key = 1000
and v._annot_key = ve._annot_key
and ve._evidenceterm_key = t._term_key
and t.abbreviation in ('ISO','ISS','ISA','ISM','IBA','IBD','IKR','IRD')
group by _marker_key
''', 'auto')
iso_annotations = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in iso_annotations:
                iso_annotations[key] = []
        iso_annotations[key].append(value)
#print(iso_annotations)

#
# do_annotations
#
results = db.sql('''
select m._marker_key, count(v._annot_key) as counter
from gomarkers m, VOC_Annot v
where m._marker_key = v._object_key
and v._annottype_key = 1023
and v._Qualifier_key != 1614157
group by _marker_key having count(v._annot_key) between 3 and 4
''', 'auto')
do_annotations = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in do_annotations:
                do_annotations[key] = []
        do_annotations[key].append(value)
#print(do_annotations)

#
# used_refs : >1 and <12
#
results = db.sql('''
select distinct m._marker_key, count(distinct c.pubmedid) as counter
from gomarkers m, VOC_Annot v, VOC_Evidence ve, VOC_Term t, BIB_Citation_Cache c
where m._marker_key = v._object_key
and v._annottype_key = 1000
and v._annot_key = ve._annot_key
and ve._evidenceterm_key = t._term_key
and t.abbreviation in ('EXP','IDA','IPI','IMP','IGI','IEP')
and ve._refs_key = c._refs_key
and c.pubmedid is not null
group by _marker_key having count(distinct c.pubmedid) between 2 and 11
''', 'auto')
used_refs = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in used_refs:
                used_refs[key] = []
        used_refs[key].append(value)
#print(used_refs)

# outstanding_refs : 
# marker exists in mrk_reference
# marker does not exists in GO Annotations
# reference exists in status = GO, Chosen/Indexed
db.sql('''
select distinct m._marker_key, r._refs_key
into temp table outstanding_refs
from gomarkers m, MRK_Reference r
where m._marker_key = r._marker_key
and not exists (select 1 from VOC_Annot a, VOC_Evidence e
        where a._AnnotType_key = 1000
        and m._Marker_key = a._Object_key
        and a._Annot_key = e._Annot_key
        and e._Refs_key = r._Refs_key
        )
and exists (select 1 from BIB_Workflow_Status wf
        where r._refs_key = wf._refs_key
        and wf._Group_key = 31576666
        and wf._Status_key in (31576671,31576673)
        and wf.isCurrent = 1
        )
''', None)
db.sql('create index idx2 on outstanding_refs(_marker_key)', None)
outstanding_refs = {}
results = db.sql('''
select _marker_key, count(_refs_key) as counter from outstanding_refs
group by _marker_key
''', 'auto')
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in outstanding_refs:
                outstanding_refs[key] = []
        outstanding_refs[key].append(value)
#print(outstanding_refs)

#
# gxd_refs : outstanding_refs && GXD/Chosen/Indexed/Full-coded <20
#
results = db.sql('''
select m._marker_key, count(distinct m._refs_key) as counter
from outstanding_refs m
where exists (select 1 from BIB_Workflow_Status wf
        where m._refs_key = wf._refs_key
        and wf._Group_key = 31576665 
        and wf._Status_key in (31576671,31576673,31576674)
        and wf.isCurrent = 1 
        )
group by m._marker_key having count(distinct m._refs_key) <20
''', 'auto')
gxd_refs = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in gxd_refs:
                gxd_refs[key] = []
        gxd_refs[key].append(value)
#print(gxd_refs)

#
# non_gxd_refs : outstanding_refs && not GXD/Chosen/Indexed/Full-coded >=20
#
results = db.sql('''
select m._marker_key, count(distinct m._refs_key) as counter
from outstanding_refs m
where not exists (select 1 from BIB_Workflow_Status wf
        where m._refs_key = wf._refs_key
        and wf._Group_key = 31576665 
        and wf._Status_key in (31576671,31576673,31576674)
        and wf.isCurrent = 1 
        )
group by m._marker_key having count(distinct m._refs_key) >=20
''', 'auto')
non_gxd_refs = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in non_gxd_refs:
                non_gxd_refs[key] = []
        non_gxd_refs[key].append(value)
#print(non_gxd_refs)

#
# after_completion : bib_refs.creation_date > go_tracking.completion_date
#
results = db.sql('''
select m._marker_key, count(distinct ve._refs_key) as counter
from gomarkers m, VOC_Annot v, VOC_Evidence ve, BIB_Workflow_Status wf, BIB_Refs r, GO_Tracking gt
where m._marker_key = v._object_key
and v._annottype_key = 1000
and v._annot_key = ve._annot_key
and ve._refs_key = wf._refs_key
and wf._Group_key = 31576666
and wf.isCurrent = 1
and ve._refs_key = r._refs_key
and m._marker_key = gt._marker_key
and r.creation_date > gt.completion_date
group by m._marker_key having count(distinct ve._refs_key) between 21 and 38
''', 'auto')
after_completion = {}
for r in results:
        key = r['_marker_key']
        value = r['counter']
        if key not in after_completion:
                after_completion[key] = []
        after_completion[key].append(value)
#print(after_completion)

#
# for all markers in gomarkers:
#       if exp_annotation, used_refs, gxd_refs & non_gxd_refs exist
#       then write marker info to fp file
#
results = db.sql('select * from gomarkers order by symbol', 'auto')
for r in results:
        
        key = r['_marker_key']

        if key not in exp_annotations:
                continue

        if key not in used_refs:
                continue

        if key not in outstanding_refs:
                continue

        if key not in gxd_refs:
                continue

        if key not in non_gxd_refs:
                continue

        fp.write(r['mgiID'] + TAB)
        fp.write(r['symbol'] + TAB)
        fp.write(r['markerType'] + TAB)
        fp.write(r['featureType'] + TAB)

        if r['completion_date'] != None:
                fp.write(str(r['completion_date']))
        fp.write(TAB)

        if key in exp_annotations:
                fp.write(str(exp_annotations[key][0]))
        fp.write(TAB)

        if key in iso_annotations:
                fp.write(str(iso_annotations[key][0]))
        fp.write(TAB)

        if key in used_refs:
                fp.write(str(used_refs[key][0]))
        fp.write(TAB)

        if key in outstanding_refs:
                fp.write(str(outstanding_refs[key][0]))
        fp.write(TAB)

        if key in used_refs and key in outstanding_refs:
                fp.write('%.2f' % (outstanding_refs[key][0]/used_refs[key][0]))
        fp.write(TAB)

        if key in after_completion:
                fp.write(str(after_completion[key][0]))
        fp.write(TAB)

        if key in gxd_refs:
                fp.write(str(gxd_refs[key][0]))
        fp.write(TAB)

        if key in non_gxd_refs:
                fp.write(str(non_gxd_refs[key][0]))
        fp.write(TAB)

        if key in do_annotations:
                fp.write(str(do_annotations[key][0]))
        fp.write(TAB)

        fp.write(CRT)

reportlib.finish_nonps(fp)

