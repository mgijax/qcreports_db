
set nocount on
go

select m._Marker_key, m.symbol, name = substring(m.name,1,100)
into #markers1
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Type_key = 1
and m._Marker_Status_key in (1,3)
and not exists (select 1 from VOC_Annot g
where g._AnnotType_key = 1000
and m._Marker_key = g._Object_key)
go

create unique clustered index index_marker_key on #markers1(_Marker_key)
go

select m.*, a.accID
into #markers2
from #markers1 m, MRK_Acc_View a
where m._Marker_key = a._Object_key
and a.prefixPart = "MGI:"
and a._LogicalDB_key = 1
and a.preferred = 1
go

create unique clustered index index_marker_key on #markers2(_Marker_key)
go

set nocount off
go

print ""
print "Mouse Genes that have Rat Homologs but no GO associations"
print ""

select distinct m.accID, m.symbol, m.name
from #markers2 m, HMD_Homology_Marker hm1, HMD_Homology h1,
HMD_Homology_Marker hm2, HMD_Homology h2, MRK_Marker m2
where m._Marker_key = hm1._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 40
order by m.symbol
go

print ""
print "Mouse Genes that have Human Homologs Only but no GO associations"
print ""

select distinct m.accID, m.symbol, m.name
from #markers2 m, HMD_Homology_Marker hm1, HMD_Homology h1,
HMD_Homology_Marker hm2, HMD_Homology h2, MRK_Marker m2
where m._Marker_key = hm1._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 2
and not exists (select 1 from HMD_Homology_Marker hm3, HMD_Homology h3, MRK_Marker m3
where h1._Class_key = h3._Class_key
and h3._Homology_key = hm3._Homology_key
and hm3._Marker_key = m3._Marker_key
and m3._Species_key not in (1,2))
order by m.symbol
go
