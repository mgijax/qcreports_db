set nocount on
go

select s._Assay_key, specimenLabel = substring(s.specimenLabel, 1, 50)
into #spec1
from GXD_Specimen s
where (s.age like '%day' or s.age like '%week' or s.age like '%month' or s.age like '%year')
go

select s._Assay_key, laneLabel = substring(s.laneLabel, 1, 50)
into #spec2
from GXD_GelLane s
where (s.age like '%day' or s.age like '%week' or s.age like '%month' or s.age like '%year')
go

select s._Assay_key, specimenLabel = substring(s.specimenLabel, 1, 50)
into #spec3
from GXD_Specimen s
where (s.age = 'Not Applicable' or s.age = 'Not Specified' or s.age = 'embryonic')
go

select s._Assay_key, laneLabel = substring(s.laneLabel, 1, 50)
into #spec4
from GXD_GelLane s
where s._GelControl_key = 1
and (s.age = 'Not Applicable' or s.age = 'Not Specified' or s.age = 'embryonic')
go

create index idx1 on #spec1(_Assay_key)
create index idx1 on #spec2(_Assay_key)
create index idx1 on #spec3(_Assay_key)
create index idx1 on #spec4(_Assay_key)
go

set nocount off
go

print ""
print "InSitu Specimens with NULL Age Value (when there should be one)"
print ""

select a.mgiID, a.jnumID, s.specimenLabel
from #spec1 s, GXD_Assay_View a
where s._Assay_key = a._Assay_key
go

print ""
print "Gel Lane Specimens with NULL Age Value (when there should be one)"
print ""

select a.mgiID, a.jnumID, s.laneLabel
from #spec2 s, GXD_Assay_View a
where s._Assay_key = a._Assay_key
go

print ""
print "InSitu Specimens with Not Applicable, Not Specified or Embryonic"
print ""

select a.mgiID, a.jnumID, s.specimenLabel
from #spec3 s, GXD_Assay_View a
where s._Assay_key = a._Assay_key
go

print ""
print "Gel Lane Specimens with Not Applicable, Not Specified or Embryonic"
print ""

select a.mgiID, a.jnumID, s.laneLabel
from #spec4 s, GXD_Assay_View a
where s._Assay_key = a._Assay_key
go

