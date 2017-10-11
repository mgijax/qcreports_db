
\echo ''
\echo 'Curation metrics for GXD, monthly for current year (so far) and last year'
\echo '- user count is defined as curators who created an assay record in the month'
\echo '- reference count is of refs having their first annotated assay in the month'
\echo ''

WITH users AS (
	SELECT extract(YEAR FROM ga.creation_date)::integer AS YEAR,
		extract(MONTH FROM ga.creation_date)::integer AS MONTH,
		count(DISTINCT ga._CreatedBy_key) AS users
	FROM gxd_assay ga, mgi_user u
	WHERE (extract(YEAR FROM now()) - extract(YEAR FROM ga.creation_date)) < 6
		and ga._CreatedBy_key = u._User_key
		and u._UserType_key = 316352
	GROUP BY 1, 2
), earliest_gxd AS (
	SELECT ga._Refs_key,
		min(ga.creation_date) AS creation_date
	FROM gxd_assay ga, gxd_expression e
	WHERE ga._Assay_key = e._Assay_key
		AND e.isForGXD = 1
	GROUP BY 1
), gxd_counts AS (
	SELECT extract(YEAR FROM creation_date)::integer AS YEAR,
		extract(MONTH FROM creation_date)::integer AS MONTH,
		count(1) AS refs_with_first_gxd_annotation
	FROM earliest_gxd
	WHERE (extract(YEAR FROM now()) - extract(YEAR FROM creation_date)) < 6
	GROUP BY 1, 2
)
SELECT e.year, e.month, u.users,
	e.refs_with_first_gxd_annotation,
	round((e.refs_with_first_gxd_annotation::float / u.users)::numeric, 2) AS refs_per_user
FROM gxd_counts e, users u
WHERE e.year = u.year
	AND e.month = u.month
ORDER BY 1 DESC, 2 DESC
;
