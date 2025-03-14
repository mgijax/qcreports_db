/* TR10731/added 'mesometrium' */

select distinct i._Specimen_key, t.stage
INTO TEMPORARY TABLE temp1
from GXD_InSituResult i, GXD_ISResultStructure r, VOC_Term s, GXD_TheilerStage t
where i._Result_key = r._Result_key
and r._EMAPA_Term_key = s._Term_key
and r._Stage_key = t._Stage_key
and not (t.stage = 28 
and s.term in ('placenta','decidua','decidua basalis','decidua capsularis', 'cumulus oophorus'))
;

select distinct _Specimen_key 
INTO TEMPORARY TABLE temp2
from temp1
group by _Specimen_key having count(*) > 1
;

select distinct i._GelLane_key, t.stage
INTO TEMPORARY TABLE temp3
from GXD_GelLane i, GXD_GelLaneStructure r, VOC_Term s, GXD_TheilerStage t
where i.age not like '%-%'
and i.age not like '%,%'
and i._GelLane_key = r._GelLane_key
and r._EMAPA_Term_key = s._Term_key
and r._Stage_key = t._Stage_key
and not (t.stage = 28 
and s.term in ('placenta','decidua','decidua basalis','decidua capsularis','uterus', 'mesometrium', 'cumulus oophorus'))
;

select distinct _GelLane_key 
INTO TEMPORARY TABLE temp4
from temp3
group by _GelLane_key having count(*) > 1
;

\echo ''
\echo 'InSitu Specimens annotated to structures of > 1 Theiler Stage'
\echo '(excludes TS28:placenta, TS28:decidua, TS28:decidua basalis, TS28:decidua capsularis, TS28:cumulus oophorus)'
\echo ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, a.modifiedby
from temp2 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

\echo ''
\echo 'Gel Lane Specimens annotated to structures of > 1 Theiler Stage'
\echo '(excludes TS28:placenta, TS28:decidua, TS28:decidua basalis, TS28:decidua capsularis, TS28:uterus, TS28:mesometrium, TS28:cumulus oophorus)'
\echo ''

select a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, a.modifiedby
from temp4 t, GXD_GelLane s, GXD_Assay_View a
where t._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

--
-- _EMAPA_term_key & _Stage_key as descendent terms
-- 	_AncetorTerm_key, _Term_key, _Stage_key
-- 	Descendents

SELECT emaps._EMAPA_Term_key as _AncestorTerm_key, 
	d_emaps._EMAPA_Term_key as _Term_key, 
	emaps._Stage_key
INTO TEMPORARY TABLE emapaChild
FROM VOC_Term_EMAPS emaps, DAG_Closure c, VOC_Term_EMAPS d_emaps
WHERE emaps._Term_key = c._AncestorObject_key
  AND c._MGIType_key = 13
  AND c._DescendentObject_key = d_emaps._Term_key
UNION
-- Top Ancestors
SELECT emaps._EMAPA_Term_key as _AncestorTerm_key, 
	emaps._EMAPA_Term_key as _Term_key, 
	emaps._Stage_key
FROM VOC_Term_EMAPS emaps
;

create index emapaChild_ancestorterm_key_idx on emapaChild(_AncestorTerm_key);
create index emapaChild_stage_key_idx on emapaChild(_Stage_key);

/* get all children of 'reproductive system' */
SELECT DISTINCT ec._Term_key, ec._Stage_key
INTO TEMPORARY TABLE repChild
FROM VOC_Term t, emapaChild ec
WHERE t._Term_key = ec._AncestorTerm_key
AND t.term = 'reproductive system'
;

/* get all children of 'female' */
SELECT DISTINCT ec._Term_key, ec._Stage_key
INTO TEMPORARY TABLE femaleChild
FROM VOC_Term t, emapaChild ec
WHERE t._Term_key = ec._AncestorTerm_key
AND t.term = 'female reproductive system'
;

/* get all children of 'male' */
SELECT DISTINCT ec._Term_key, ec._Stage_key
INTO TEMPORARY TABLE maleChild
FROM VOC_Term t, emapaChild ec
WHERE t._Term_key = ec._AncestorTerm_key
AND t.term = 'male reproductive system'
;

/* get info about 'reproductive system;female' and children */
select distinct s._Specimen_key, s.specimenLabel, a.jnumID, a.mgiID, a.modifiedby
INTO TEMPORARY TABLE fSpecimens
from GXD_Specimen s, GXD_Assay_View a, GXD_InSituResult ir, GXD_ISResultStructure irs, femaleChild f
where s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and s._Specimen_key = ir._Specimen_key
and ir._Result_key = irs._Result_key
and irs._EMAPA_Term_key = f._Term_key
and irs._Stage_key = f._Stage_key
;

/* get info about 'reproductive system;male' and children */
select distinct s._Specimen_key
INTO TEMPORARY TABLE mSpecimens
from GXD_Specimen s, GXD_Assay_View a, GXD_InSituResult ir, GXD_ISResultStructure irs, maleChild m
where s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and s._Specimen_key = ir._Specimen_key
and ir._Result_key = irs._Result_key
and irs._EMAPA_Term_key = m._Term_key
and irs._Stage_key = m._Stage_key
;

\echo ''
\echo 'InSitu Specimens and Gel Lanes with > 1 Sex' 
\echo '(excludes J:80502)'
\echo ''

/* report all specimens with annotated to both male and female structures */
select distinct mgiID, jnumID, substring(specimenLabel,1,50) as specimenLabel, f.modifiedby
from fSpecimens f, mSpecimens m
where f._Specimen_key = m._Specimen_key
and f.jnumID not in ('J:80502')
order by mgiID, jnumID,specimenLabel
;

