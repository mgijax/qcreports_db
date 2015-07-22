select e._Annot_key, e.evidenceCode
into #goevidence
from VOC_Annot a, VOC_Evidence_View e
where a._AnnotType_key = 1000
and a._Annot_key = e._Annot_key
go

select distinct a._Object_key, e.evidenceCode
into #gomarker
from VOC_Annot a, VOC_Evidence_View e
where a._AnnotType_key = 1000
and a._Annot_key = e._Annot_key
go

\echo ''
\echo 'Total # of Annotations by GO Evidence Code'
\echo ''

select count(_Annot_key) as "# of Annotations", evidenceCode
from #goevidence
group by evidenceCode
go

\echo ''
\echo 'Number of Markers Per GO Evidence Code'
\echo ''

select count(_Object_key) as "# of Markers", evidenceCode
from #gomarker
group by evidenceCode
go

