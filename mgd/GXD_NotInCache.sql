set nocount on
go

select a._Assay_key
into #missing
from GXD_Assay a
where not exists (select e.* from GXD_Expression e
where a._Assay_key = e._Assay_key)
go

set nocount off
go

print ""
print "GXD Assays entirely missing from GXD Expression Cache Table"
print "(and therefore not visible in Web interface)"
print ""

select mgiID, jnumID, assayType
from #missing m, GXD_Assay_View v
where m._Assay_key = v._Assay_key
go

print ""
print "Gel GXD Assays entirely missing from GXD Expression Cache Table"
print "(due to missing Gel Lane Structures)"
print ""

select a.mgiID, a.jnumID, a.assayType
from #missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 1
and not exists (select gl.* from GXD_GelLaneStructure_View gl
where a._Assay_key = gl._Assay_key)
go

print ""
print "InSitu GXD Assays entirely missing from GXD Expression Cache Table"
print "(due to missing Specimen Results)"
print ""

select a.mgiID, a.jnumID, a.assayType
from #missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 0
and not exists (select s.* from GXD_Specimen s, GXD_InSituResult r
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key)
go

print ""
print "InSitu GXD Assays entirely missing from GXD Expression Cache Table"
print "(due to missing Specimen Results or Results Structures)"
print ""

select a.mgiID, a.jnumID, a.assayType
from #missing m, GXD_Assay_View a
where m._Assay_key = a._Assay_key
and a.isGelAssay = 0
and not exists (select s.* from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key
and r._Result_key = rs._Result_key)
go

set nocount on
go

select r._Result_key, r._Specimen_key
into #imissingstructs
from GXD_InSituResult r
where not exists
(select 1 from GXD_ISResultStructure s
where r._Result_key = s._Result_key)
go

set nocount off
go

print ""
print "InSitu Results missing Structures"
print ""

select a.mgiID, a.jnumID, specimenLabel = substring(s.specimenLabel, 1, 50)
from #imissingstructs r, GXD_Specimen s, GXD_Assay_View a
where r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
go

set nocount on
go

select g._GelLane_key
into #gmissingstructs
from GXD_GelLane g
where g._GelControl_key = 1
and not exists
(select 1 from GXD_GelLaneStructure s
where g._GelLane_key = s._GelLane_key)
go

set nocount off
go

print ""
print "Gel Results missing Structures"
print ""

select a.mgiID, a.jnumID, laneLabel = substring(s.laneLabel, 1, 50)
from #gmissingstructs r, GXD_GelLane s, GXD_Assay_View a
where r._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
go

select g._GelLane_key
into #gmissingbands
from GXD_GelLane g
where g._GelControl_key = 1
and not exists
(select 1 from GXD_GelBand b
where g._GelLane_key = b._GelLane_key)
go

set nocount off
go

print ""
print "Gel Results missing Bands"
print ""

select a.mgiID, a.jnumID, laneLabel = substring(s.laneLabel, 1, 50)
from #gmissingbands r, GXD_GelLane s, GXD_Assay_View a
where r._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
go

