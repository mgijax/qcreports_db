set nocount on
go

select p._Probe_key, p.name, pm._Marker_key, caccID = pa.accID, maccID = ma.accID
into #clone
from PRB_Probe p, PRB_Marker pm, ACC_Accession pa, ACC_Accession ma
where p.name like 'IMAGE clone%'
and p._Probe_key = pm._Probe_key
and pm.relationship = "E"
and p._Probe_key = pa._Object_key
and pa._MGIType_key = 3
and pa.prefixPart = "MGI:"
and pa._LogicalDB_key = 1
and pa.preferred = 1
and pm._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma.prefixPart = "MGI:"
and ma._LogicalDB_key = 1
and ma.preferred = 1
go

set nocount off
go

print ""
print "IMAGE Clones with Seq IDs which do not exist for encoding Markers"
print ""

select distinct c.caccID "Clone", c.maccID "Marker", a.accID
from #clone c, PRB_AccRef_View a
where c._Probe_key = a._Object_key
and a._LogicalDB_key = 9
and not exists (select 1 from MRK_AccRef_View ma
where c._Marker_key = ma._Object_key
and ma.accID = a.accID)
order by c.caccID
go

print ""
print "Markers with Seq IDs which do not exist for Clones to which the Marker encodes"
print ""

select distinct c.maccID "Marker", c.caccID "Clone", a.accID
from #clone c, MRK_AccRef_View a
where c._Marker_key = a._Object_key
and a._LogicalDB_key = 9
and not exists (select 1 from PRB_AccRef_View ma
where c._Probe_key = ma._Object_key
and ma.accID = a.accID)
order by c.maccID
go

set nocount on
go

drop table #clone
go

select p._Probe_key, pm._Marker_key, a.accID
into #clone
from PRB_Probe p, PRB_Marker pm, ACC_Accession a, ACC_Accession ma
where p.name like 'IMAGE clone%'
and p._Probe_key = pm._Probe_key
and pm.relationship != "E"
and p._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._LogicalDB_key = 9
and pm._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 9
and ma.accID = a.accID
go

set nocount off
go

print ""
print "IMAGE Clones with Seq IDs which exist for non-encoding Markers"
print ""

select distinct ca.accID "Clone", ma.accID "Marker", c.accID
from #clone c, ACC_Accession ca, ACC_Accession ma
where c._Probe_key = ca._Object_key
and ca._MGIType_key = 3
and ca.prefixPart= "MGI:"
and ca._LogicalDB_key = 1
and ca.preferred = 1
and c._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma.prefixPart= "MGI:"
and ma._LogicalDB_key = 1
and ma.preferred = 1
order by ca.accID
go

