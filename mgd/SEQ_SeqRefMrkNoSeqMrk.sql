
set nocount on
go

select _Object_key
into #exclude
from ACC_Accession
where accID in ("J:23000", "J:25000", "J:56000", "J:56550", "J:57656", "J:57747", "J:58000", "J:60000", 
		"J:63846", "J:66660", "J:66661", "J:67226", "J:68100", "J:71600", "J:72245", "J:72246", 
		"J:72247", "J:72400", "J:72460", "J:73065", "J:73796", "J:75000", "J:77000", "J:78475",
                "J:79300", "J:79330", "J:80000", "J:80001", "J:80155", "J:80162", "J:81858", "J:82000",
		"J:82718", "J:82808", "J:86335", "J:87348", "J:87916", "J:88305", "J:91912", "J:94121")
go

create index idx1 on #exclude(_Object_key)
go

/* reference/sequence pairs where */
/*    the reference is associated with a marker */
/*    and the sequence is not associated with any marker */

select ra._Refs_key, ra._Object_key
into #refs1
from MGI_Reference_Assoc ra, ACC_Accession sa
where ra._MGIType_key = 19
and ra._Object_key = sa._Object_key
and sa._MGIType_key = 19
and sa._LogicalDB_key = 9
and sa.preferred = 1
and not exists (select 1 from #exclude e where ra._Refs_key = e._Object_key)
and exists (select 1 from MRK_Reference mr where ra._Refs_key = mr._Refs_key)
and not exists (select 1 from SEQ_Marker_Cache mc where ra._Object_key = mc._Sequence_key)
go

create index idx1 on #refs1(_Refs_key)
create index idx2 on #refs1(_Object_key)
go

/* reference/sequence pairs where */
/*    the sequence is not associated with a Probe */
/*    or the sequence is associated with a Probe that has a Null relationship with a Marker */
/*    or the sequence is associated with a Probe that has no relationship to a Marker */

/* the sequence is associated with a Probe that has a Null relationship with a Marker */

select r._Refs_key, r._Object_key, pm._Probe_key
into #refs2
from #refs1 r, SEQ_Probe_Cache pc, PRB_Marker pm
where r._Object_key = pc._Sequence_key
and pc._Probe_key = pm._Probe_key
and pm.relationship = null
go

/*  the sequence is associated with a Probe that has no relationship to a Marker */

insert into #refs2
select r._Refs_key, r._Object_key, pc._Probe_key
from #refs1 r, SEQ_Probe_Cache pc
where r._Object_key = pc._Sequence_key
and not exists (select 1 from PRB_Marker pm where pc._Probe_key = pm._Probe_key)
go

/*  the sequence is not associated with a Probe */

insert into #refs2
select r._Refs_key, r._Object_key, -1
from #refs1 r
where not exists (select 1 from SEQ_Probe_Cache pc where r._Object_key = pc._Sequence_key)
go

create index idx1 on #refs2(_Refs_key)
create index idx2 on #refs2(_Object_key)
create index idx3 on #refs2(_Probe_key)
go

/* select distinct references/sequences */

select distinct _Refs_key, _Object_key
into #refs3
from #refs2
go

create index idx1 on #refs3(_Refs_key)
create index idx2 on #refs3(_Object_key)
go

/* store counts */

select _Refs_key, num_seqs = count(_Object_key)
into #refs4
from #refs3
group by _Refs_key
go

create index idx1 on #refs4(_Refs_key)
create index idx2 on #refs4(num_seqs)
go

/* distinct references */

select distinct _Refs_key into #refs5 from #refs1
go
create index idx1 on #refs5(_Refs_key)
go

/* references with marker associations where the marker has no sequence annotations */

select r._Refs_key, mr._Marker_key
into #refs6
from #refs5 r, MRK_Reference mr
where r._Refs_key = mr._Refs_key
and not exists (select 1 from SEQ_Marker_Cache mc where mr._Marker_key = mc._Marker_key)
go

create index idx1 on #refs6(_Refs_key)
create index idx2 on #refs6(_Marker_key)
go

set nocount off
go

print ""
print "    Sequence References Associated with Markers but no Sequence/Marker"
print ""
print "A row in this report represents a Sequence Reference that is associated with a Marker and "
print "    a.  the Sequence is not associated with any Marker "
print " and "
print "    a.  the Sequence is not associated with a Probe OR "
print "    b.  the Sequence is associated with a Probe that has a NULL relationship with a Marker OR "
print "    c.  the Sequence is associated with a Probe that has no relationship with a Marker "
print ""
print "All that is displayed is the reference and the number of sequences associated with it."
print "Only displays references with less than 500 sequences."
print ""

select a.accID, numberOfSequences = r.num_seqs
from #refs4 r, ACC_Accession a
where r.num_seqs < 500
and r._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
order by r.num_seqs desc, a.numericPart
go

print ""
print "================================================================================"
print ""
print "A row in this section represents a Sequence/Marker where"
print "    a.  the Reference is associated with a Sequence and a Marker"
print "    b.  the Sequence is not associated with any Marker "
print "    c.  the Marker associated with the Reference (a) has no Sequence Annotations"
print ""

select b.accID, m.accID
from #refs6 r, ACC_Accession b, ACC_Accession m
where r._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = "J:"
and r._Marker_key = m._Object_key
and m._MGIType_key = 2
and m._LogicalDB_key = 1
and m.prefixPart = "MGI:"
and m.preferred = 1
order by b.numericPart
go

print ""
print "================================================================================"
print ""
print "A row in this section represents a Sequence/Reference/Probe where"
print "    a.  the Reference is associated with a Sequence and a Marker"
print "    b.  the Sequence is not associated with any Marker "
print " and "
print "    c.  the Sequence is associated with a Probe that has a NULL relationship with a Marker OR "
print "    d.  the Sequence is associated with a Probe that has no relationship with a Marker "
print ""

select distinct s.accID, b.accID, p.accID
from #refs2 r, ACC_Accession s, ACC_Accession b, ACC_Accession p
where r._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = "J:"
and r._Object_key = s._Object_key
and s._MGIType_key = 19
and s.preferred = 1
and r._Probe_key = p._Object_key
and p._MGIType_key = 3
and p._LogicalDB_key = 1
and p.prefixPart = "MGI:"
and p.preferred = 1
go

