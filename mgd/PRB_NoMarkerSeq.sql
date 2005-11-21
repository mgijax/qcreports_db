set nocount on
go

/* Select all Probes of Source 'mouse, laboratory' which contain */
/* at least one non-autoE encoding gene */

select p._Probe_key, pm._Marker_key
into #probes1
from PRB_Probe p, PRB_Source s, PRB_Marker pm
where p._Source_key = s._Source_key 
and s._Organism_key = 1
and p._Probe_key = pm._Probe_key 
and pm.relationship = "E"
and pm._Refs_key != 86302
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

/* resolve probe name and marker symbol */

select p._Probe_key, p._Marker_key, pp.name, m.symbol
into #probes3
from #probes2 p, PRB_Probe pp, MRK_Marker m
where p._Probe_key = pp._Probe_key
and p._Marker_key = m._Marker_key
go

create index idx1 on #probes3(_Probe_key)
go

/* Retrieve unique Sequence Accession ID/Reference (J:) pairs */
/* for each Marker by using its associated Probe */

select p.name, p.symbol, p._Probe_key, p._Marker_key, a.accID, r._Refs_key
into #markers1
from #probes3 p, ACC_Accession a, ACC_AccessionReference r
where p._Probe_key = a._Object_key 
and a._MGIType_key = 3
and a._LogicalDB_key = 9 
and a._Accession_key = r._Accession_key
go

create index idx1 on #markers1(_Marker_key)
create index idx2 on #markers1(_Probe_key)
create index idx3 on #markers1(_Refs_key)
go


/* Retrieve Markers that have a Sequence association via the Accession table */

select m.*
into #markers2
from #markers1 m
where exists
(select 1 from ACC_Accession a
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 9
and m.accID = a.accID)
go

create index idx1 on #markers2(_Marker_key)
create index idx2 on #markers2(_Probe_key)
create index idx3 on #markers2(_Refs_key)
create index idx4 on #markers2(name)
go

/* Retrieve the Marker/Sequence association and compare the references */

select m.*, refs2 = r._Refs_key
into #markers3
from #markers2 m, ACC_Accession a, ACC_AccessionReference r
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 9
and m.accID = a.accID
and a._Accession_key = r._Accession_key
and m._Refs_key != r._Refs_key
go

create index idx1 on #markers3(_Refs_key)
create index idx2 on #markers3(refs2)
create index idx3 on #markers3(name)
go

set nocount off
go

print ""
print "Molecular Segments with Encoding Markers and Sequence IDs"
print "and no corresponding Marker-Sequence ID association"
print ""

select m.name, m.symbol, m.accID
from #markers1 m
where not exists (select 1 from #markers2 mm where m._Marker_key = mm._Marker_key and m._Probe_key = mm._Probe_key)
order by m.name
go

print ""
print "Molecular Segments with Encoding Markers and Sequence IDs"
print "and corresponding Marker-Sequence ID association w/ a different Reference"
print ""

select m.name, m.symbol, m.accID, b1.accID, b2.accID
from #markers3 m, ACC_Accession b1, ACC_Accession b2
where m._Refs_key = b1._Object_key
and b1._LogicalDB_key = 1
and b1.prefixPart = "J:"
and m.refs2 = b2._Object_key
and b2._LogicalDB_key = 1
and b2.prefixPart = "J:"
order by m.name
go

