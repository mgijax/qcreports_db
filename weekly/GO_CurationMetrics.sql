
\echo ''
\echo 'Curation metrics for GO, monthly for current year (so far) and the previous five years'
\echo '- user count is defined as curators who created a GO annotation in the month'
\echo '- reference count is of refs having their first GO annotation in the month'
\echo ''

WITH users AS (
	SELECT extract(YEAR FROM ve.creation_date)::integer AS YEAR,
		extract(MONTH FROM ve.creation_date)::integer AS MONTH,
		count(DISTINCT ve._CreatedBy_key) AS users
	FROM voc_annot va, voc_evidence ve, mgi_user u
	WHERE va._AnnotType_key = 1000
		AND va._Annot_key = ve._Annot_key
		and ve._CreatedBy_key = u._User_key
		and u._UserType_key = 316352
		AND (extract(YEAR FROM now()) - extract(YEAR FROM ve.creation_date)) < 6
	GROUP BY 1, 2 ORDER BY 1 DESC, 2 DESC
), earliest_annot AS (
	SELECT ve._Refs_key,
		min(ve.creation_date) AS creation_date
	FROM voc_annot va, voc_evidence ve
	WHERE va._AnnotType_key = 1000
		AND va._Annot_key = ve._Annot_key
	GROUP BY 1
), ref_counts AS (
	SELECT extract(YEAR FROM creation_date)::integer AS YEAR,
		extract(MONTH FROM creation_date)::integer AS MONTH,
		count(1) AS refs_with_first_go_annotation
	FROM earliest_annot
	WHERE (extract(YEAR FROM now()) - extract(YEAR FROM creation_date)) < 6
GROUP BY 1, 2
ORDER BY 1 DESC, 2 DESC
)
SELECT u.year, u.month, u.users,
	c.refs_with_first_go_annotation,
	round((c.refs_with_first_go_annotation::float / u.users)::numeric, 2) AS refs_per_user
FROM users u, ref_counts c
WHERE u.year = c.year
	AND u.month = c.month
ORDER BY 1 DESC, 2 DESC
;
