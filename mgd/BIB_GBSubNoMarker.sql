print ""
print "GenBank Submission References with no Marker associations"
print ""

select a.accID
from BIB_Refs b, ACC_Accession a
where b.journal = 'GenBank Submission'
and b._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
and not exists (select 1 from MRK_Reference r
where b._Refs_key = r._Refs_key)
order by accID
go
