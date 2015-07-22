select r._Refs_key
into #refs1
from BIB_Refs r
where r.year >= 1975
and datalength(r.abstract) = 0 
go

create index refs1_idx on #refs1(_Refs_key)
go

select r._Refs_key, a.accID
into #refs2
from #refs1 r, ACC_Accession a
where r._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 29
go

create index refs2_idx on #refs2(_Refs_key)
go

select r.*
into #refs3
from #refs2 r
where not exists
(select n.* from BIB_Notes n
where r._Refs_key = n._Refs_key and lower(n.note) like '%no abstract available%')
go

create index refs3_idx on #refs3(_Refs_key)
go

\echo ''
\echo 'References w/ PubMed ID and No Abstract (where publication year >= 1975)'
\echo ''

select r.accID, c.jnum, substring(c.short_citation, 1, 50) as short_citation
from #refs3 r, BIB_All_View c
where r._Refs_key = c._Refs_key
group by r.accID, c.jnum, short_citation
order by min(c.year), min(c._primary)
go
 
