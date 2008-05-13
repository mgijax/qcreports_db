set nocount on
go

select s._Assay_key, specimenLabel = substring(s.specimenLabel, 1, 50)
into #spec1
from GXD_Specimen s
where (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

select s._Assay_key, laneLabel = substring(s.laneLabel, 1, 50)
into #spec2
from GXD_GelLane s
where s._GelControl_key = 1
and (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

create index idx1 on #spec1(_Assay_key)
create index idx1 on #spec2(_Assay_key)
go

set nocount off
go

print ""
print "InSitu Specimens with Not Applicable, Not Specified"
print ""

select mgiID = a1.accID, jnumID = a2.accID, s.specimenLabel
from #spec1 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
and ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Marker_key = a1._Object_key
and a1._MGIType_key = 2
and a1._LogicalDB_key = 1
and a1.prefixPart = "MGI:"
and a1.preferred = 1
and ga._Refs_key = a2._Object_key
and a2._MGIType_key = 2
and a2._LogicalDB_key = 1
and a2.prefixPart = "J:"
and a2.preferred = 1
go

print ""
print "Gel Lane Specimens with Not Applicable, Not Specified"
print ""

select mgiID = a1.accID, jnumID = a2.accID, s.laneLabel
from #spec2 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
and ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Marker_key = a1._Object_key
and a1._MGIType_key = 2
and a1._LogicalDB_key = 1
and a1.prefixPart = "MGI:"
and a1.preferred = 1
and ga._Refs_key = a2._Object_key
and a2._MGIType_key = 2
and a2._LogicalDB_key = 1
and a2.prefixPart = "J:"
and a2.preferred = 1
go

set nocount on
go

select distinct s._Specimen_key
into #temp1
from GXD_Specimen s, GXD_InSituResult i, GXD_ISResultStructure r, GXD_Structure c, GXD_TheilerStage t
where s.age like 'postnatal%'
and s._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Structure_key = c._Structure_key
and c._Stage_key = t._Stage_key
and t.stage != 28
go

select distinct i._GelLane_key
into #temp2
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_Structure s, GXD_TheilerStage t
where i.age like 'postnatal%'
and i._GelLane_key = r._GelLane_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and t.stage != 28
go

set nocount off
go

print ""
print "InSitu Specimens with Adult Specimens annotated to embryonic structures"
print ""

select a.mgiID, a.jnumID, specimenLabel = substring(s.specimenLabel, 1, 50)
from #temp1 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

print ""
print "Gel Lane Specimens with Adult Specimens annotated to embryonic structures"
print ""

select a.mgiID, a.jnumID, laneLabel = substring(s.laneLabel, 1, 50)
from #temp2 t, GXD_GelLane s, GXD_Assay_View a
where t._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go
