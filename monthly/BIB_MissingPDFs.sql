\echo ''
\echo 'J#''s missing PDF''s'
\echo 'Includes references which:'
\echo '  1. have a type of Peer Reviewed Article'
\echo '  2. have no PDF file'
\echo '  3. have a J: number'
\echo ''

with refs_without_pdfs as (
select c.numericPart as jnum_numeric, c.jnumid, c.short_citation
from bib_refs r, voc_term t, bib_workflow_data d, bib_citation_cache c
where r._ReferenceType_key = t._Term_key
	and t.term = 'Peer Reviewed Article'
	and r._Refs_key = d._Refs_key
	and r._Refs_key = c._Refs_key
	and d.hasPDF = 0
order by 1 desc
)
select jnumid, short_citation
from refs_without_pdfs
;
