\echo ''
\echo 'Dagger character in title'
\echo ''
\echo 'Directions:'
\echo ''
\echo 'If the word "dagger" or the phrase "double dagger" is at the end of the title, it is usually because there is an icon at the end of the title that Pubmed changes to the word "dagger".'
\echo ''
\echo 'Check the pdf - if the word dagger is not part of the title, then remove it from the title field in the database. There may also be parentheses that should be removed.'
\echo ''

select c.mgiid, r.title
from bib_refs r, bib_citation_cache c
where
(r.title like '%double dagger%' or r.title like '%dagger.' or r.title like '%dagger..' or r.title like '%(dagger).')
and r._refs_key = c._refs_key
order by c.mgiid

