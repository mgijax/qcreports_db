set nocount on
go

/* Select all Probes of Source 'mouse, laboratory' which contain */
/* at least one encoding gene */

select p._Probe_key, pm._Marker_key
into #probes1
from PRB_Probe p, PRB_Source s, PRB_Marker pm
where p._Source_key = s._Source_key 
and s._Organism_key = 1
and p._Probe_key = pm._Probe_key 
and pm.relationship = "E"
go

create index idx1 on #probes1(_Probe_key)
go

/* Select all Probes with one and only one encoding Marker */

select _Probe_key, _Marker_key
into #probes2
from #probes1 
group by _Probe_key having count(*) = 1
go

create index idx1 on #probes2(_Probe_key)
create index idx2 on #probes2(_Marker_key)
go

select distinct p._Probe_key, p._Marker_key, pp.name, m.symbol
into #probes3
from #probes2 p, PRB_Probe pp, MRK_Marker m
where p._Probe_key = pp._Probe_key
and p._Marker_key = m._Marker_key
go

create index idx1 on #probes3(_Probe_key)
go

/* Retrieve unique Sequence Accession ID/Reference (J:) pairs */
/* for each Marker by using its associated Probe */

select p.name, p.symbol, p._Marker_key, a.accID, ar._Refs_key, jnumID = b.accID
into #markers1
from #probes3 p, ACC_Accession a, ACC_AccessionReference ar, ACC_Accession b
where p._Probe_key = a._Object_key 
and a._MGIType_key = 3
and a._LogicalDB_key = 9 
and a._Accession_key = ar._Accession_key
and ar._Refs_key = b._Object_key
and b._MGIType_key = 1
and b.prefixPart = "J:"
and b._LogicalDB_key = 1
go

create index idx1 on #markers1(name)
create index idx2 on #markers1(symbol)
create index idx3 on #markers1(accID)
create index idx4 on #markers1(jnumID)
go

select distinct p.name, p.symbol, p._Marker_key, p.accID, p._Refs_key, p.jnumID
into #markers2
from #markers1 p
go

create index idx1 on #markers2(name)
create index idx2 on #markers2(_Marker_key)
create index idx3 on #markers2(_Refs_key)
go

set nocount off
go

print ""
print "Molecular Segments with Encoding Markers and Sequence IDs"
print "and no corresponding Marker-Sequence ID association"
print ""

select m.name, m.symbol, m.accID
from #markers2 m
where not exists
(select 1 from ACC_Accession a
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 9
and m.accID = a.accID)
order by m.name
go

print ""
print "Molecular Segments with Encoding Markers and Sequence IDs"
print "and corresponding Marker-Sequence ID association w/ a different Reference"
print ""

select m.name, m.symbol, m.accID, m.jnumID, b.accID
from #markers2 m, ACC_Accession a, ACC_AccessionReference r, BIB_ACC_View b
where m._Marker_key = a._Object_key
and a._LogicalDB_key = 9
and m.accID = a.accID
and a._MGIType_key = 2
and a._Accession_key = r._Accession_key
and m._Refs_key != r._Refs_key
and r._Refs_key = b._Object_key
and b.prefixPart = "J:"
order by m.name
go

