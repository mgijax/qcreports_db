
set nocount on
go

select v._Object_key, substring(m.name,1,50) as name, substring(m.symbol,1,25) as symbol, m._Marker_Type_key
into #nongene
from VOC_Annot v, MRK_Marker m
where v._AnnotType_key = 1000
and v._Object_key = m._Marker_key
and m._Marker_Type_key != 1
go

create index idx1 on #nongene(_Object_key)
go

select distinct _Object_key, name, symbol, _Marker_Type_key, count(_object_key) as annotations
into #nongeneout
from #nongene 
group by _Object_key
go

create index idx1 on #nongeneout(_Object_key)
create index idx2 on #nongeneout(_Marker_Type_key)
go

select a.accID, substring(t.name,1,25) as type, m.symbol, m.name, m.annotations
into #toPrint
from #nongeneout m, ACC_Accession a, MRK_Types t
where m._Marker_Type_key = t._Marker_Type_key
and m._Object_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 1
and a.prefixPart = "MGI:"
and a.preferred = 1
go

print ""
print "Non-Gene Markers with GO Annotations"
print ""

select "Number of unique MGI Gene IDs:  ", count(distinct accID) from #toPrint
union
select "Number of total rows:  ", count(*) from #toPrint
go

set nocount off
go

print ""

select * from #toPrint order by name
go

