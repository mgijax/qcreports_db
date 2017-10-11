
\echo ''
\echo 'Number of new J: numbers assigned per month for current year (so far) and the previous five years'
\echo ''

select extract(year from creation_date)::integer as year,
	extract(month from creation_date)::integer as month,
	count(1) as new_jnumbers
from acc_accession a
where _MGIType_key = 1
	and a.prefixPart = 'J:'
	and a._LogicalDB_key = 1
	and (extract(year from now()) - extract(year from creation_date)) < 6
group by 1, 2
order by 1 desc, 2 desc
;
