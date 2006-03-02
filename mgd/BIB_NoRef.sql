
set nocount on
go

select b._Refs_key
into #refs
from BIB_Refs b
where not exists (select 1 from MRK_Reference r where b._Refs_key = r._Refs_key)
go
create index idx1 on #refs(_Refs_key)
go

select _Refs_key into #strains from MGI_Reference_Assoc where _MGIType_key = 10
go
create index idx1 on #strains(_Refs_key)
go

select b._Refs_key, strain = 'no '
into #refs2
from #refs b
where not exists (select 1 from #strains r where b._Refs_key = r._Refs_key)
go

insert into #refs2
select b._Refs_key, strain = 'yes'
from #refs b
where exists (select 1 from #strains r where b._Refs_key = r._Refs_key)
go

create index idx1 on #refs2(_Refs_key)
go

set nocount off
go

print ""
print "References w/no Marker Attached"
print ""

select b.jnum, substring(b.short_citation, 1, 75), b.year, r.strain
from #refs2 r, BIB_All_View b
where r._Refs_key = b._Refs_key
order by b.year, b._primary
go
