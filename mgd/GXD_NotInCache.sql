select a._Assay_key
INTO TEMPORARY TABLE missing
from GXD_Assay a
where a._AssayType_key in (1,2,3,4,5,6,8,9)
and not exists (select e.* from GXD_Expression e
where a._Assay_key = e._Assay_key)
;

\echo ''
\echo 'GXD Assays entirely missing from GXD Expression Cache Table'
\echo '(and therefore not visible in Web interface)'
\echo ''

select mgiID, jnumID, assayType, modifiedBy
from missing m, GXD_Assay_View v
where m._Assay_key = v._Assay_key
order by jnumID, assayType, mgiID
;

\echo ''
\echo 'Gel GXD Assays entirely missing from GXD Expression Cache Table'
\echo '(due to missing Gel Lane Structures)'
\echo ''

select a.mgiID, a.jnumID, a.assayType, modifiedBy
from missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 1
and not exists (select gl.* from GXD_GelLaneStructure_View gl
where a._Assay_key = gl._Assay_key)
order by jnumID, assayType, mgiID
;

\echo ''
\echo 'InSitu GXD Assays entirely missing from GXD Expression Cache Table'
\echo '(due to missing Specimen Results)'
\echo ''

select a.mgiID, a.jnumID, a.assayType, modifiedBy
from missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 0
and not exists (select s.* from GXD_Specimen s, GXD_InSituResult r
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key)
order by jnumID, assayType, mgiID
;

\echo ''
\echo 'InSitu GXD Assays entirely missing from GXD Expression Cache Table'
\echo '(due to missing Specimen Results or Results Structures)'
\echo ''

select a.mgiID, a.jnumID, a.assayType, modifiedBy
from missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 0
and not exists (select s.* from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key
and r._Result_key = rs._Result_key)
order by jnumID, assayType, mgiID
;

select r._Result_key, r._Specimen_key
INTO TEMPORARY TABLE imissingstructs
from GXD_InSituResult r
where not exists
(select 1 from GXD_ISResultStructure s
where r._Result_key = s._Result_key)
;

\echo ''
\echo 'InSitu Results missing Structures'
\echo ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, modifiedBy
from imissingstructs r, GXD_Specimen s, GXD_Assay_View a
where r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
order by jnumID, mgiID, specimenLabel
;

select r._Specimen_key
INTO TEMPORARY TABLE imissingresults
from GXD_Specimen r
where not exists
(select 1 from GXD_InSituResult s
where r._Specimen_key = s._Specimen_key)
and not exists
(select 1 from missing m where r._Assay_key = m._Assay_key)
;

\echo ''
\echo 'InSitu Specimens missing Results'
\echo ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, modifiedBy
from imissingresults r, GXD_Specimen s, GXD_Assay_View a
where r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
order by jnumID, mgiID, specimenLabel
;

select g._GelLane_key
INTO TEMPORARY TABLE gmissingstructs
from GXD_GelLane g, VOC_Term t
where g._GelControl_key = t._Term_key and t.term = 'No'
and not exists
(select 1 from GXD_GelLaneStructure s
where g._GelLane_key = s._GelLane_key)
;

\echo ''
\echo 'Gel Results missing Structures'
\echo ''

select a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, modifiedBy
from gmissingstructs r, GXD_GelLane s, GXD_Assay_View a
where r._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
order by jnumID, mgiID, laneLabel
;

select g._GelLane_key
INTO TEMPORARY TABLE gmissingbands
from GXD_GelLane g, VOC_Term t
where g._GelControl_key = t._Term_key and t.term = 'No'
and not exists
(select 1 from GXD_GelBand b
where g._GelLane_key = b._GelLane_key)
;

\echo ''
\echo 'Gel Results missing Bands'
\echo ''

select a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, modifiedBy
from gmissingbands r, GXD_GelLane s, GXD_Assay_View a
where r._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
order by jnumID, mgiID, laneLabel
;

