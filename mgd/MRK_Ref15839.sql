set nocount on
go

/* select distinct Markers/Refs from MLC_Reference (duplicates may exist) */

select _Marker_key, _Refs_key
into tempdb..allReferences
from MRK_Reference
union
select distinct _Marker_key, _Refs_key
from MLC_Reference
go

create nonclustered index index_Marker_key on tempdb..allReferences(_Marker_key)
go

/* select Markers w/ single reference */

select distinct _Marker_key, _Refs_key
into #single
from tempdb..allReferences
group by _Marker_key
having count(*) = 1
go

set nocount off
go

print ""
print "Markers w/ single Reference = J:15839"
print ""

select m.symbol, m.chromosome
from #single s, MRK_Marker m, BIB_View b
where s._Marker_key = m._Marker_key
and s._Refs_key = b._Refs_key
and b.jnum = 15839
order by m.chromosome, m.symbol
go

drop table tempdb..allReferences
go

