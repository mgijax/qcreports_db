print ""
print "Invalid RefSeq IDs Associated to Mouse Markers"
print ""

select a.accID, m.symbol, u.login
from ACC_Accession a, ACC_AccessionReference r, MRK_Marker m, MGI_User u
where a._LogicalDB_key = 27 
and a.prefixPart not in ('XM_', 'XR_')
and a._MGIType_key = 2
and a._Object_key = m._Marker_key
and m._Organism_key = 1
and a._Accession_key = r._Accession_key
and r._Refs_key not in (53672, 64047)
and a._CreatedBy_key = u._User_key
go

