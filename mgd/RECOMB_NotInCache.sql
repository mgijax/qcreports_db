select a._Assay_key
INTO TEMPORARY TABLE missing
from GXD_Assay a
where a._AssayType_key in (10,11)
and not exists (select e.* from GXD_Expression e
where a._Assay_key = e._Assay_key)
;

\echo ''
\echo 'Assays entirely missing from cache table'
\echo '(and therefore not visible in Web interface)'
\echo ''

select mgiID, jnumID, assayType
from missing m, GXD_Assay_View v
where m._Assay_key = v._Assay_key
;

\echo ''
\echo 'Recombinant/transgenic assays entirely missing from cache table'
\echo '(due to missing Specimen Results)'
\echo ''

select a.mgiID, a.jnumID, a.assayType
from missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 0
and not exists (select s.* from GXD_Specimen s, GXD_InSituResult r
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key)
;

\echo ''
\echo 'Recombinant/transgenic assays entirely missing from cache table'
\echo '(due to missing Specimen Results or Results Structures)'
\echo ''

select a.mgiID, a.jnumID, a.assayType
from missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 0
and not exists (select s.* from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key
and r._Result_key = rs._Result_key)
;

select r._Result_key, r._Specimen_key
INTO TEMPORARY TABLE imissingstructs
from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r
where a._AssayType_key in (10,11)
and a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key
and not exists
(select 1 from GXD_ISResultStructure i
where r._Result_key = i._Result_key)
;

\echo ''
\echo 'InSitu Results missing Structures'
\echo ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from imissingstructs r, GXD_Specimen s, GXD_Assay_View a
where r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
;

select r._Specimen_key
INTO TEMPORARY TABLE imissingresults
from GXD_Assay a, GXD_Specimen r
where a._AssayType_key in (10,11)
and a._Assay_key = r._Assay_key
and not exists
(select 1 from GXD_InSituResult s
where r._Specimen_key = s._Specimen_key)
and not exists
(select 1 from missing m where r._Assay_key = m._Assay_key)
;

\echo ''
\echo 'InSitu Specimens missing Results'
\echo ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from imissingresults r, GXD_Specimen s, GXD_Assay_View a
where r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
;

