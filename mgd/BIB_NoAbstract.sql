-- all refs newer than 1974 and have a Jnumber
select r._Refs_key
INTO TEMPORARY TABLE refs1
from BIB_Refs r, ACC_Accession a
where r.year >= 1975
and r.abstract is null
and r._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LOgicalDB_key = 1
and a.preferred = 1
and a.prefixPart = 'J:'
;

create index refs1_idx on refs1(_Refs_key)
;

-- all refs that have PMID
select r._Refs_key, a.accID
INTO TEMPORARY TABLE refs2
from refs1 r, ACC_Accession a
where r._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 29
;

create index refs2_idx on refs2(_Refs_key)
;

-- exclude refs with no abstract in note
select r.*
INTO TEMPORARY TABLE refs3
from refs2 r
where not exists
(select n.* from BIB_Notes n
where r._Refs_key = n._Refs_key and lower(n.note) like '%no abstract% available%')
;

create index refs3_idx on refs3(_Refs_key)
;

-- exclude refs with MGI:NoAbstract tag
select r.*
INTO TEMPORARY TABLE refs4
from refs3 r
where not exists
(select 1 from BIB_Workflow_Tag wt
where r._Refs_key = wt._Refs_key and wt._Tag_key = 31576719)
;

create index refs4_idx on refs4(_Refs_key)
;

\echo ''
\echo 'References w/ PubMed ID and No abstract (where publication year >= 1975). Excludes MGI:NoAbstract tag and No Abstract note '
\echo ''

select r.accID, c.jnum, substring(c.short_citation, 1, 50) as short_citation
from refs4 r, BIB_All_View c
where r._Refs_key = c._Refs_key
group by r.accID, c.jnum, short_citation
order by min(c.year), min(c._primary)
;
 
