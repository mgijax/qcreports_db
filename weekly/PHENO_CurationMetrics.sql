
\echo ''
\echo 'Curation metrics for Pheno, monthly for current year (so far) and the previous five years'
\echo '- user count is defined as curators who did any of these in the month:'
\echo '   = created an allele record,'
\echo '   = indexed a reference,'
\echo '   = added an MP annotation, or'
\echo '   = added a reference as original, molecular, or transmission'
\echo '- If a reference is indexed, is used for an MP annotation, and is flagged '
\echo '  as original, molecular, or transmission, then it would count in all '
\echo '  three columns (and thus three times in the total_activities column).'
\echo ''

with pheno_curator_list as (
	select distinct extract(YEAR FROM ga.creation_date)::integer AS YEAR,
		extract(MONTH FROM ga.creation_date)::integer AS MONTH,
		ve._CreatedBy_key as _User_key
	FROM voc_annot ga, voc_evidence ve
	WHERE ga._AnnotType_key = 1002
		AND ga._Annot_key = ve._Annot_key
		AND (extract(YEAR FROM now()) - extract(YEAR FROM ga.creation_date)) < 6
	union
	select distinct extract(YEAR FROM a.creation_date)::integer AS YEAR,
		extract(MONTH FROM a.creation_date)::integer AS MONTH,
		a._CreatedBy_key as _User_key
	FROM all_allele a
	WHERE (extract(YEAR FROM now()) - extract(YEAR FROM a.creation_date)) < 6
	union
	select distinct extract(YEAR FROM a.creation_date)::integer AS YEAR,
		extract(MONTH FROM a.creation_date)::integer AS MONTH,
		a._CreatedBy_key as _User_key
	FROM mgi_reference_assoc a
	WHERE a._RefAssocType_key in (1011, 1012, 1013, 1023)
		AND (extract(YEAR FROM now()) - extract(YEAR FROM a.creation_date)) < 6
	)
select year, month, count(distinct u._User_key) as active_curators
into temp table pheno_curators
from pheno_curator_list pc, mgi_user u
where pc._User_key = u._User_key
	and u._UserType_key in (316352)
group by 1, 2
;

select extract(YEAR FROM creation_date)::integer AS YEAR,
	extract(MONTH FROM creation_date)::integer AS MONTH,
	count(distinct _Refs_key) as indexed_refs
into temporary table indexed_refs
from mgi_reference_assoc
where _RefAssocType_key = 1013
	and (extract(YEAR FROM now()) - extract(YEAR FROM creation_date)) < 6
group by 1, 2
;

select extract(YEAR FROM creation_date)::integer AS YEAR,
	extract(MONTH FROM creation_date)::integer AS MONTH,
	count(distinct _Refs_key) as primary_refs
into temporary table primary_refs
from mgi_reference_assoc
where _RefAssocType_key in (1011, 1012, 1023)
	and (extract(YEAR FROM now()) - extract(YEAR FROM creation_date)) < 6
group by 1, 2
;

select extract(YEAR FROM ve.creation_date)::integer AS YEAR,
	extract(MONTH FROM ve.creation_date)::integer AS MONTH,
	count(distinct ve._Refs_key) as refs_in_mp_annotations
into temporary table refs_in_mp_annotations
from voc_annot va, voc_evidence ve
where va._AnnotType_key = 1002
	and va._Annot_key = ve._Annot_key
	and (extract(YEAR FROM now()) - extract(YEAR FROM ve.creation_date)) < 6
group by 1, 2
;

select pc.year, pc.month, i.indexed_refs, p.primary_refs,
	a.refs_in_mp_annotations,
	(i.indexed_refs + p.primary_refs + a.refs_in_mp_annotations) as total_activities,
	pc.active_curators,
	round(((i.indexed_refs + p.primary_refs + a.refs_in_mp_annotations) / pc.active_curators::float)::numeric, 2) as activies_per_curator
from pheno_curators pc,
	indexed_refs i,
	primary_refs p,
	refs_in_mp_annotations a
where pc.year = i.year and pc.month = i.month
	and pc.year = a.year and pc.month = a.month
	and pc.year = p.year and pc.month = p.month
order by 1 desc, 2 desc
;