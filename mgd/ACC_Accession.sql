print ""
print "Invalid LocusLink IDs"
print ""

select _Accession_key, accID, prefixPart, numericPart, creation_date
from ACC_Accession
where _LogicalDB_key = 24 and prefixPart is not null and prefixPart != "LOC"
go

print ""
print "Invalid RefSeq IDs"
print ""

select _Accession_key, accID, prefixPart, numericPart, creation_date
from ACC_Accession
where _LogicalDB_key = 27 and prefixPart not in ('NM_', 'NP_', 'NR_', 'XM_', 'XP_', 'XR_')
go

