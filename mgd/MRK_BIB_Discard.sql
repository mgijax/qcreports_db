\echo ''
\echo 'References that are marked as "MGI discard" and have data associated with them'
\echo ''

select distinct mm.symbol, mm.name, c.jnumid, c.pubmedid, c.mgiid, c.short_citation
from MRK_Reference m, bib_citation_Cache c, MRK_Marker mm
where m._Refs_key = c._Refs_key
and c.relevanceterm != 'keep'
and m._Marker_key = mm._Marker_key
order by mm.symbol
;

select distinct t.name, c.jnumid, c.pubmedid, c.mgiid, c.short_citation
from VOC_Annot a, VOC_Evidence e, BIB_Citation_Cache c, VOC_Annottype t
where e._Annot_key = a._Annot_key
and a._Annottype_key = t._Annottype_key
and e._Refs_key = c._Refs_key
and c.relevanceterm != 'keep'
order by t.name
;
