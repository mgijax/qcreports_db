
set nocount on
go

select distinct ra._Refs_key, num_seqs = count(ra._Object_key)
into #refs
from MGI_Reference_Assoc ra, SEQ_Sequence_ACC_View sa
where ra._MGIType_key = 19
and ra._Object_key = sa._Object_key
and sa._LogicalDB_key = 9
and sa.preferred = 1
and exists (select 1 from  MRK_Reference mr
where ra._Refs_key = mr._Refs_key)
and not exists (select 1 from SEQ_Marker_Cache smc
                where ra._Object_key = smc._Sequence_key
                and ra._Refs_key = smc._Refs_key)
group by ra._Refs_key
go

set nocount off
go

print ""
print "    Sequence References Associated with Markers but no Sequence/Marker"
print ""
print "A row in this report represents a Sequence Reference that is associated"
print "with a Marker but the Sequence itself is not associated with any"
print "Marker via the Reference.  All that is displayed is the reference and "
print "the number of sequences it is associated with.  Only displays "
print "references with less than 500 sequences."
print ""

select jNumber = b.jnumID, numberOfSequences = r.num_seqs
from #refs r, BIB_View b
where r._Refs_key = b._Refs_key 
and r.num_seqs < 500
order by r.num_seqs DESC, b.jnumID
go

