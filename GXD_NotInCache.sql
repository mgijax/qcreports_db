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
print "GXD Assays missing from GXD Expression Cache Table"
print "(and therefore not visible in Web interface)"
print ""

select mgiID, jnumID, assayType
from #missing m, GXD_Assay_View v
where m._Assay_key = v._Assay_key
go

print ""
print "Gel GXD Assays missing from GXD Expression Cache Table"
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
print "InSitu GXD Assays missing from GXD Expression Cache Table"
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
print "InSitu GXD Assays missing from GXD Expression Cache Table"
print "(due to missing Specimen Result Structures)"
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

