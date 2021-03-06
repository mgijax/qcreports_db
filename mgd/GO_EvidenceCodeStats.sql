select e._Annot_key, e.evidenceCode
INTO TEMPORARY TABLE goevidence
from VOC_Annot a, VOC_Evidence_View e
where a._AnnotType_key = 1000
and a._Annot_key = e._Annot_key
;

select distinct a._Object_key, e.evidenceCode
INTO TEMPORARY TABLE gomarker
from VOC_Annot a, VOC_Evidence_View e
where a._AnnotType_key = 1000
and a._Annot_key = e._Annot_key
;

\echo ''
\echo 'Total  of Annotations by GO Evidence Code'
\echo ''

select count(_Annot_key) as " of Annotations", evidenceCode
from goevidence
group by evidenceCode
;

\echo ''
\echo 'Number of Markers Per GO Evidence Code'
\echo ''

select count(_Object_key) as " of Markers", evidenceCode
from gomarker
group by evidenceCode
;

