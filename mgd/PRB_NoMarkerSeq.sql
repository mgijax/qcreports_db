set nocount on
go

/* Select all Probes of Source 'mouse, laboratory' which contain */
/* at least one encoding gene */

select distinct p._Probe_key, p.name, pm._Marker_key, m.symbol
into tempdb..probes1
from PRB_Probe p, PRB_Source s, PRB_Marker pm, MRK_Marker m 
where p._Source_key = s._Source_key 
and s._ProbeSpecies_key = 1
and p._Probe_key = pm._Probe_key 
and pm.relationship = "E" 
and pm._Marker_key = m._Marker_key
go

create nonclustered index pk on tempdb..probes1(_Probe_key)
go

/* Select all Probes with one and only one encoding Marker */

select * 
into tempdb..probes2
from tempdb..probes1 
group by _Probe_key having count(*) = 1
go

create nonclustered index pk on tempdb..probes2(_Probe_key)
go

/* Retrieve unique Sequence Accession ID/Reference (J:) pairs */
/* for each Marker by using its associated Probe */

select distinct p.name, p.symbol, p._Marker_key, a.accID, ar._Refs_key, jnumID = b.accID
into #markers
from tempdb..probes2 p, ACC_Accession a, ACC_AccessionReference ar, BIB_Acc_View b 
where p._Probe_key = a._Object_key 
and a._MGIType_key = 3
and a._LogicalDB_key = 9 
and a._Accession_key = ar._Accession_key
and ar._Refs_key = b._Object_key
and b.prefixPart = "J:"
go

drop table tempdb..probes1
go

drop table tempdb..probes2
go

set nocount off
go

print ""
print "Molecular Segments with Encoding Markers and Sequence IDs"
print "and no corresponding Marker-Sequence ID association"
print ""

select m.name, m.symbol, m.accID
from #markers m
where not exists
(select 1 from MRK_AccRef_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_key = 9
and m.accID = a.accID)
order by m.name
go

print ""
print "Molecular Segments with Encoding Markers and Sequence IDs"
print "and corresponding Marker-Sequence ID association w/ a different Reference"
print ""

select m.name, m.symbol, m.accID, m.jnumID "Molecular Ref", b.accID "Marker Ref"
from #markers m, MRK_AccRef_View a, BIB_Acc_View b
where m._Marker_key = a._Object_key
and a._LogicalDB_key = 9
and m.accID = a.accID
and m._Refs_key != a._Refs_key
and a._Refs_key = b._Object_key
and b.prefixPart = "J:"
order by m.name
go

