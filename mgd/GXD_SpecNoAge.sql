set nocount on
go

select s._Assay_key, specimenLabel = substring(s.specimenLabel, 1, 50)
into #spec1
from GXD_Specimen s
where s.age like 'postnatal [0-9]%'
go

select s._Assay_key, laneLabel = substring(s.laneLabel, 1, 50)
into #spec2
from GXD_GelLane s
where s.age like 'postnatal [0-9]%'
go

select s._Assay_key, specimenLabel = substring(s.specimenLabel, 1, 50)
into #spec3
from GXD_Specimen s
where (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

select s._Assay_key, laneLabel = substring(s.laneLabel, 1, 50)
into #spec4
from GXD_GelLane s
where s._GelControl_key = 1
and (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

create index idx1 on #spec1(_Assay_key)
create index idx1 on #spec2(_Assay_key)
create index idx1 on #spec3(_Assay_key)
create index idx1 on #spec4(_Assay_key)
go

set nocount off
go

print ""
print "InSitu Specimens with incorrect 'postnatal' entry"
print ""

select mgiID = a1.accID, jnumID = a2.accID, s.specimenLabel
from #spec1 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
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
print "Gel Lane Specimens with incorrect 'postnatal' entry"
print ""

select mgiID = a1.accID, jnumID = a2.accID, s.laneLabel
from #spec2 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
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
print "InSitu Specimens with Not Applicable, Not Specified"
print ""

select mgiID = a1.accID, jnumID = a2.accID, s.specimenLabel
from #spec3 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
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
from #spec4 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
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

