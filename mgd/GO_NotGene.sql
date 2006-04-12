
set nocount on
go

select v._Object_key, name = substring(m.name,1,50), symbol = substring(m.symbol,1,25), m._Marker_Type_key
into #nongene
from VOC_Annot v, MRK_Marker m
where v._AnnotType_key = 1000
and v._Object_key = m._Marker_key
and m._Marker_Type_key != 1
go

create index idx1 on #nongene(_Object_key)
go

select distinct _Object_key, name, symbol, _Marker_Type_key, annotations = count(_object_key) 
into #nongeneout
from #nongene 
group by _Object_key
go

create index idx1 on #nongeneout(_Object_key)
create index idx2 on #nongeneout(_Marker_Type_key)
go

set nocount off
go

print ""
print "Non-Gene Markers with GO Annotations"
print ""

select a.accID, type = substring(t.name,1,25), m.symbol, m.name, m.annotations
from #nongeneout m, ACC_Accession a, MRK_Types t
where m._Marker_Type_key = t._Marker_Type_key
and m._Object_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 1
and a.prefixPart = "MGI:"
and a.preferred = 1
order by t.name
go

