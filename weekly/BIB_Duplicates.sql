\echo ''
\echo 'References with Duplicate Titles'
\echo 'Includes references which meet all of the following criteria:'
\echo '  1. match title (case insensitive) with another reference'
\echo '  2. match journal (case insensitive) with the same reference as #1'
\echo '  3. has type other than MGI Direct Data Submission, Newsletter, Personal Communication, External Resource, or MGI Curation Record'
\echo '  4. either have a null DOI ID or a DOI ID that does not match a reference that satisfies the above three criteria'

select _Refs_key, lower(btrim(title)) as title, lower(btrim(journal)) as journal
into temp table lower_refs
from bib_refs
where title not like '%.'
union
select _Refs_key, lower(substring(btrim(title), 1, length(title) - 1)) as title, lower(btrim(journal)) as journal
from bib_refs
where title like '%.'
;

create index idx1 on lower_refs(title)
;

create index idx2 on lower_refs(journal)
;

create unique index idx3 on lower_refs(_Refs_key)
;

select c.numericPart as jnum_numeric, c.jnumid, c.pubmedid, c.doiid, b.title, b.journal, b.issue,
	b.vol, b.pgs, b.authors
from lower_refs r, bib_citation_cache c, bib_refs b, voc_term t
where r._Refs_key = c._Refs_key
	and r._Refs_key = b._Refs_key
	and b._ReferenceType_key = t._Term_key
	and t.term not in ('MGI Direct Data Submission', 'Newsletter', 'Personal Communication',
		'External Resource', 'MGI Curation Record')
	and exists (select 1 from lower_refs r2, bib_citation_cache c2
		where r._Refs_key != r2._Refs_key
		and r.journal = r2.journal
		and r.title = r2.title
		and r2._Refs_key = c2._Refs_key
		and ((c.doiid != c2.doiid) or (c2.doiid is null) or (c.doiid is null))
		)
order by b.title, b.journal, c.numericPart
;
