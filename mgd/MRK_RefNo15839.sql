set nocount on
go

/* Only Markers w/ 1 Reference */

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
 
/* History Incomplete */

select distinct r._Marker_key, r._Refs_key
into #markers3
from #single r, MRK_History h
where r._Marker_key = h._Marker_key
and (h._Refs_key is null
or h.name is null
or h.creation_date is null)
go

set nocount off
go

print ""
print "Markers w/ single Reference != J#15839"
print ""

select m.symbol, m.chromosome
from #markers3 r, MRK_Marker m, BIB_View b
where r._Marker_key = m._Marker_key
and r._Refs_key = b._Refs_key
and b.jnum != 15839
order by m.chromosome, m.symbol
go

drop table tempdb..allReferences
go

