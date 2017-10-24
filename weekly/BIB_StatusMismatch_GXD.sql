\echo ''
\echo 'References with GXD Status not matching curation data'
\echo 'Includes references which:'
\echo '  1. have a current GXD status other than Indexed or Full-coded'
\echo '  2. have a J: number'
\echo '  3. meet at least one of these two criteria:'
\echo '     a. is in GXD Lit Index'
\echo '     b. is associated with an expression assay, excluding CRE'
\echo ''

with gxd_unused as (
	select r._Refs_key, j.numericPart, j.accid, g.abbreviation as group, t.term as status
	from bib_refs r, acc_accession j, bib_workflow_status s, voc_term g, voc_term t
	where r._Refs_key = j._Object_key
		and j._MGIType_key = 1
		and j.prefixPart = 'J:'
		and j._LogicalDB_key = 1
		and r._Refs_key = s._Refs_key
		and s.isCurrent = 1
		and s._Group_key = g._Term_key
		and g.abbreviation = 'GXD'
		and s._Status_key = t._Term_key
		and t.term not in ('Indexed', 'Full-coded')
)
select distinct u.accid, u.group, u.status,
	case
		when (a._Assay_key is not null) then 'yes'
		else ''
	end has_gxd_assays,
	case
		when (i._Index_key is not null) then 'yes'
		else ''
	end in_gxd_index
from gxd_unused u
left outer join gxd_assay a on (u._Refs_key = a._Refs_key)
left outer join gxd_index i on (u._Refs_key = i._Refs_key)
where (a._Assay_key is not null
	and a._AssayType_key not in (10,11))
	or i._Index_key is not null
order by u.accid
;
