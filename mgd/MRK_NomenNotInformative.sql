set nocount on
go

select m._Marker_key, m.symbol, category = 'a'
into #markers
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Status_key = 1
and (m.symbol like '[A-Z][0-9][0-9][0-9][0-9][0-9]' 
or m.symbol like '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]')
union
select m._Marker_key, m.symbol, category = 'b'
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Status_key = 1
and m.symbol like '%Rik'
and m.name like 'RIKEN%'
union
select m._Marker_key, m.symbol, category = 'c'
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Status_key = 1
and m.name like 'DNA segment%'
go

create clustered index idx_key on #markers(_Marker_key)
go

select m.*, a.accID
into #sequences
from #markers m, MRK_AccRef_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_key = 9
and a._Refs_key = 64047
go

set nocount off
go

print ""
print "MGI Marker with Uninformative Nomenclature"
print "where symbol is:"
print "   a) GenBank Accession ID"
print "   b) RIKEN symbol"
print "   c) DNA segment"
print "where symbol has acquired a Sequence Accession ID from LocusLink"
print "where symbol has no homology entry in MGI"
print ""

select m.symbol, m.accID, m.category
from #sequences m
where not exists (select 1 from HMD_Homology_Marker h where m._Marker_key = h._Marker_key)
order by m.category
go

