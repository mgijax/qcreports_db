\echo ''
\echo 'References with A&P Status not matching curation data'
\echo 'Includes references which:'
\echo '  1. have a current AP status other than Indexed or Full-coded'
\echo '  2. have a J: number'
\echo '  3. meet at least one of these three criteria:'
\echo '     a. indexed to an allele'
\echo '     b. flagged as transmission, original, or molecular ref for an allele'
\echo '     c. used as evidence for an MP annotation'
\echo ''

with ap_unused as (
	select r._Refs_key, j.numericPart, j.accid, g.abbreviation as group, t.term as status
	from bib_refs r, acc_accession j, bib_workflow_status s, voc_term g, voc_term t
	where r._Refs_key = j._Object_key
		and j._MGIType_key = 1
		and j.prefixPart = 'J:'
		and j._LogicalDB_key = 1
		and r._Refs_key = s._Refs_key
		and s.isCurrent = 1
		and s._Group_key = g._Term_key
		and g.abbreviation = 'AP'
		and s._Status_key = t._Term_key
		and t.term not in ('Indexed', 'Full-coded')
)
select distinct u.accid, u.group, u.status,
	case 
		when (a._Annot_key is not null) then 'yes'
		else ''
	end has_MP_annotation,
	case 
		when (i._Assoc_key is not null) then 'yes'
		else ''
	end is_indexed_to_allele,
	case
		when (x._Assoc_key is not null) then 'yes'
		else ''
	end original_molecular_or_transmission
from ap_unused u
left outer join voc_evidence e on (u._Refs_key = e._Refs_key)
left outer join voc_annot a on (e._Annot_key = a._Annot_key and a._AnnotType_key = 1002)
left outer join mgi_reference_assoc i on (u._Refs_key = i._Refs_key and i._RefAssocType_key = 1013)
left outer join mgi_reference_assoc x on (u._Refs_key = x._Refs_key and x._RefAssocType_key in (1011, 1012, 1023))
where a._Annot_key is not null
	or i._Assoc_key is not null
	or x._Assoc_key is not null
order by u.accid
;
