
\echo ''
\echo 'Curation metrics for GXD, monthly for current year (so far) and in the previous five years'
\echo '- user count is defined as curators who created an assay during the month'
\echo ''

select extract(year from ga.creation_date)::integer AS year,
  extract(month from ga.creation_date)::integer AS month,
  count(distinct ga._CreatedBy_key) as users
into temp table gxd_users
from gxd_assay ga, mgi_user u
where (extract(year from now()) - extract(year from ga.creation_date)) < 6
  and ga._CreatedBy_key = u._User_key
  and u._UserType_key = 316352
group by 1, 2
;
select ga._Refs_key, min(ga.creation_date) AS creation_date
into temp table earliest_assays
from gxd_assay ga, gxd_expression e
where ga._Assay_key = e._Assay_key
	and e.isForGXD = 1
group by 1
;
select extract(year from creation_date)::integer AS year,
	extract(month from creation_date)::integer AS month,
	count(1) AS refs_with_first_gxd_annotation
into temp table assay_counts
from earliest_assays
where (extract(year from now()) - extract(year from creation_date)) < 6
group by 1, 2
;
select u.year, u.month, u.users,
	a.refs_with_first_gxd_annotation, 
	round((a.refs_with_first_gxd_annotation::float / u.users)::numeric, 2) AS refs_coded_per_user
from gxd_users u, assay_counts a
where a.year = u.year and a.month = u.month
order by 1 desc, 2 desc
;
