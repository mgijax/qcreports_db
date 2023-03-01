\echo ''
\echo 'References Missing DOI number'
\echo '  1. Reference has no doi ID'
\echo '  2. Reference has status of “Keep”'
\echo '  3. Reference Type = “Peer Reviewed Article”'
\echo '  4. is_review = “no”'
\echo '  5. reference creation date   >11/01/2017 '
\echo '  6. exclude journals “Mol Vis” and “Am J Trans Res”'
\echo '  7. Reference does not have “MGI:DOI_checked” tag associated'

select c.mgiid, c.pubmedid, c.jnumid
from bib_citation_cache c, bib_refs b
where c.doiid is null
and c.relevanceterm = 'keep'
and c.referencetype = 'Peer Reviewed Article'
and c.isreviewarticle = 0
and c.journal not in ('Mol Vis', 'Am J Trans Res')
and c._refs_key = b._refs_key
and b.creation_date::date >= '11/01/2017'
and not exists (select 1 from bib_workflow_tag wt 
        where c._refs_key = wt._refs_key
        and wt._tag_key = 111834743
        )
order by c.mgiid
;
