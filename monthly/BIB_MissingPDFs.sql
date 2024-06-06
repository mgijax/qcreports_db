\echo ''
\echo 'J#''s missing PDF''s'
\echo 'Includes references which:'
\echo '  1. have a type of Peer Reviewed Article'
\echo '  2. have no PDF file'
\echo '  3. have a J: number'
\echo 'Excludes references which'
\echo '  1. have status = “Discard”'
\echo '  2. have tags = “MGI:no_pdf_avail” or “MGI:hard_copy_avail”'
\echo ''

with refs_without_pdfs as (
select c.numericPart as jnum_numeric, c.jnumid, c.short_citation
from bib_refs r, voc_term t, bib_workflow_data d, bib_citation_cache c
where r._ReferenceType_key = t._Term_key
and t.term = 'Peer Reviewed Article'
and r._Refs_key = d._Refs_key
and r._Refs_key = c._Refs_key
and d.hasPDF = 0
and d._ExtractedText_key = 48804490
and c._relevance_key != 70594666
and not exists (select 1 from bib_workflow_tag tg , voc_term tgv
        where r._refs_key = tg._refs_key
        and tg._tag_key = tgv._term_key
        and tgv.term in ('MGI:hard_copy_avail', 'MGI:no_pdf_avail')
        )
order by 1 desc
)
select distinct jnumid, short_citation
from refs_without_pdfs
;
