print ""
print "InSitu Specimens with NULL Age Value (when there should be one)"
print ""

select a.mgiID, a.jnumID, specimenLabel = substring(s.specimenLabel, 1, 50)
from GXD_Specimen s, GXD_Assay_View a
where (s.age like '%day' or s.age like '%week' or s.age like '%month' or s.age like '%year')
and s._Assay_key = a._Assay_key
go

print ""
print "Gel Lane Specimens with Adult Specimens annotated to embryonic structures"
print "(excludes stage 28)"
print ""

select a.mgiID, a.jnumID, laneLabel = substring(s.laneLabel, 1, 50)
from GXD_GelLane s, GXD_Assay_View a
where (s.age like '%day' or s.age like '%week' or s.age like '%month' or s.age like '%year')
and s._Assay_key = a._Assay_key
go
