print ""
print "All GenBank IDs in MGI associated with a Molecular Segment or Mouse Gene"
print ""

select distinct a.accID
from ACC_Accession a
where a._LogicalDB_key = 9
and a._MGIType_key = 3
union
select distinct a.accID
from ACC_Accession a, MRK_Marker m
where a._LogicalDB_key = 9
and a._MGIType_key = 2
and a._Object_key = m._Marker_key
and m._Species_key = 1
order by a.accID
go

