set nocount on
go

/* Select Probes/Markers which hybridize to only one Marker, excluding Amplifies */

select * 
into #markers
from PRB_Marker
where relationship != 'A'
group by _Probe_key
having count(*) = 1
go

/* Select Probes where Sequence presented in paper */

select p.*
into #probes
from #markers p, PRB_Reference pr
where p._Probe_key = pr._Probe_key
and pr.hasSequence = 1
go

/* Select all of those Probes where no Sequence Acc ID exists */

select p.*
into #noaccs
from #probes p
where not exists (select a.* from ACC_Accession a
where p._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._LogicalDB_key = 9
go

/* From this list of Probes w/out Seq Acc IDs, */
/* select those where there exists other Probes attached to */
/* the same Genes which DO have a Sequence Acc ID */

select distinct n._Probe_key
into #remove
from #noaccs n, PRB_Marker pm, PRB_Probe p, ACC_Accession a
where n._Marker_key = pm._Marker_key
and pm._Probe_key = p._Probe_key
and p._Probe_key != n._Probe_key
and p._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._LogicalDB_key = 9
go

/* Remove the Probes w/ Sequence Acc ID attached thru other Probes */

delete #noaccs
from #noaccs a, #remove r
where r._Probe_key = a._Probe_key
go

/* Get some detail information for the records */

select distinct probeName = substring(p.name, 1, 20), m.chromosome, symbol,
markerName = substring(m.name, 1, 40), pr._Refs_key
into #summary
from #noaccs s, PRB_Probe p, PRB_Reference pr, PRB_Marker pm, MRK_Marker m
where s._Probe_key = p._Probe_key
and p._Probe_key = pr._Probe_key
and p._Probe_key = pm._Probe_key
and pm._Marker_key = m._Marker_key
go
 
set nocount off
go

print ""
print "Probes - No GenBank IDs - Sequence in Paper - Other Probes for Same Marker DO NOT Have GenBank IDs - Reference >= 1997"
print ""

select s.probeName "Probe", s.chromosome "Chr", s.symbol "Marker", s.markerName "Marker Name", 
b.jnum "J#", substring(b.short_citation, 1, 40) "Reference"
from #summary s, BIB_All_View b
where s._Refs_key = b._Refs_key
and b.year >= 1997
order by s.chromosome
go

