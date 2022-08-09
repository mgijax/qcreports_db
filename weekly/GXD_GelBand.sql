
select l._Assay_key, l._GelLane_key
INTO TEMPORARY TABLE assay
from GXD_GelLane l, GXD_GelBand b, VOC_Term t1, VOC_Term t2
where l._GelControl_key = t1._Term_key and t1.term = 'No'
and l._GelLane_key = b._GelLane_key
and b._Strength_key = t2._Term_key and t2.term = 'Not Applicable'
;

create index idx1 on assay(_Assay_key)
;

\echo ''
\echo 'GXD Blot w/ Control = No and Strength = Not Applicable for all bands'
\echo ''

select distinct a.jnum, a.mgiID, a.modifiedBy
from assay s, GXD_Assay_View a
where s._Assay_key = a._Assay_key
and not exists (select 1 from GXD_GelLane l, GXD_GelBand b, VOC_Term t
	where s._Assay_key = l._Assay_key
	and s._GelLane_key = l._GelLane_key
	and l._GelLane_key = b._GelLane_key
	and b._Strength_key = t._term_key and t.term != 'Not Applicable')
order by a.jnum
;

