
\echo ''
\echo 'Indexing metrics for GXD, monthly for current year (so far) and in the previous five years'
\echo '- user count is defined as curators who created an index record in the month'
\echo '- references counted for a month are those with their first lit index record in that month'
\echo ''

select extract(year from gi.creation_date)::integer AS year,
  extract(month from gi.creation_date)::integer AS month,
  count(distinct gi._CreatedBy_key) as users
into temp table gxd_users
from gxd_index gi, mgi_user u
where (extract(year from now()) - extract(year from gi.creation_date)) < 6
  and gi._CreatedBy_key = u._User_key
  and u._UserType_key = 316352
group by 1, 2
;
select ga._Refs_key, min(ga.creation_date) AS creation_date
into temp table earliest_indexed
from gxd_index ga
group by 1
;
select extract(year from creation_date)::integer AS year,
	extract(month from creation_date)::integer AS month,
	count(1) AS refs_with_first_gxd_index
into temp table index_counts
from earliest_indexed
where (extract(year from now()) - extract(year from creation_date)) < 6
group by 1, 2
;
select u.year, u.month, u.users,
	i.refs_with_first_gxd_index,
	round((i.refs_with_first_gxd_index::float / u.users)::numeric, 2) AS refs_indexed_per_user
from gxd_users u, index_counts i
where i.year = u.year and i.month = u.month
order by 1 desc, 2 desc
;
