
set nocount on
go

select distinct m._Object_key, m._Refs_key, b.jnumID, b.short_citation
into #reference
from MGI_Reference_Assoc m, MGI_RefAssocType t, BIB_Citation_Cache b
where m._MGIType_key = 11
and m._RefAssocType_key = t._RefAssocType_key
and t.assocType = "Sequence"
and m._Refs_key = b._Refs_key
go

set nocount off
go

print ""
print "Reference associations created by the gene trap load"
print ""

select jnumID, substring(short_citation, 1, 75) "citation", count(_Object_key) "number of allele records"
from #reference
group by jnumID, short_citation
order by short_citation
go

