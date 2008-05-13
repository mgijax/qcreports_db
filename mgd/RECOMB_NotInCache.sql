set nocount on
go

select a._Assay_key
into #missing
from GXD_Assay a
where a._AssayType_key in (10,11)
and not exists (select e.* from GXD_Expression e
where a._Assay_key = e._Assay_key)
go

set nocount off
go

print ""
print "Assays entirely missing from cache table"
print "(and therefore not visible in Web interface)"
print ""

select mgiID, jnumID, assayType
from #missing m, GXD_Assay_View v
where m._Assay_key = v._Assay_key
go

print ""
print "Recombinant/transgenic assays entirely missing from cache table"
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
print "Recombinant/transgenic assays entirely missing from cache table"
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

select r._Specimen_key
into #imissingresults
from GXD_Specimen r
where not exists
(select 1 from GXD_InSituResult s
where r._Specimen_key = s._Specimen_key)
and not exists
(select 1 from #missing m where r._Assay_key = m._Assay_key)
go

set nocount off
go

print ""
print "InSitu Specimens missing Results"
print ""

select a.mgiID, a.jnumID, specimenLabel = substring(s.specimenLabel, 1, 50)
from #imissingresults r, GXD_Specimen s, GXD_Assay_View a
where r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
go

