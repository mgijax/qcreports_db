set nocount on
go

select subRef = r1._Refs_key, nonsubRef = r2._Refs_key, m1._Marker_key
into #references
from BIB_Refs r1, BIB_Refs r2, MRK_Reference m1, MRK_Reference m2
where r1.journal = 'GenBank Submission'
and r2.journal != 'GenBank Submission'
and r1._primary = r2._primary
and r1._Refs_key = m1._Refs_key
and r2._Refs_key = m2._Refs_key
and m1._Marker_key = m2._Marker_key
go

set nocount off
go

print ""
print "Markers w/ GenBank Submission References which match non-GenBank Submission References"
print "(Matches are performed using First Author)"
print ""

select m.symbol, b1.accID "Submission J:", b2.accID "Non-Submission J:"
from #references r, MRK_Marker m, ACC_Accession b1, ACC_Accession b2
where r._Marker_key = m._Marker_key
and r.subRef = b1._Object_key
and b1._MGIType_key = 1
and b1.prefixPart = "J:"
and b1._LogicalDB_key = 1
and r.nonsubRef = b2._Object_key
and b2._MGIType_key = 1
and b2.prefixPart = "J:"
and b2._LogicalDB_key = 1
go
