set nocount on
go

select m._Marker_key, m.symbol, name = substring(m.name,1,50), category = 'a'
into #markers
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and (m.symbol like '[A-Z][0-9][0-9][0-9][0-9][0-9]' 
or m.symbol like '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]')
union
select m._Marker_key, m.symbol, name = substring(m.name,1,50), category = 'b'
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m.symbol like '%Rik'
and m.name like 'RIKEN%'
union
select m._Marker_key, m.symbol, name = substring(m.name,1,50), category = 'c'
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m.name like 'DNA segment%'
go

create clustered index idx_key on #markers(_Marker_key)
go

/* symbol has acquired a Sequence Accession ID from LocusLink */

select m.*
into #sequences1
from #markers m
where exists (select 1 from MRK_AccRef_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_key = 9
and a._Refs_key = 64047)
go

create index idx_key on #sequences1(_Marker_key)
go

select sq.*, s.synonym, jnumID = a.accID
into #sequences2
from #sequences1 sq, MGI_Synonym s, MGI_SynonymType st, ACC_Accession a
where sq._Marker_key = s._Object_key
and s._SynonymType_key = st._SynonymType_key
and st.synonymType = "exact"
and s._Refs_key != null
and s._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
and a.preferred = 1
union
select sq.*, null, null
from #sequences1 sq
where not exists (select 1 from MGI_Synonym s, MGI_SynonymType st
where sq._Marker_key = s._Object_key
and s._SynonymType_key = st._SynonymType_key
and st.synonymType = "exact")
go

create index idx_key on #sequences2(_Marker_key)
go

set nocount off
go

print ""
print "MGI Markers with Uninformative Nomenclature"
print "where symbol is:"
print "   a) GenBank Accession ID"
print "   b) RIKEN symbol"
print "   c) DNA segment"
print "where symbol has acquired a Sequence Accession ID from LocusLink"
print "where symbol has no homology entry in MGI"
print ""

select distinct m.symbol, m.name, m.category, m.synonym, m.jnumID
from #sequences2 m
where not exists (select 1 from HMD_Homology_Marker h where m._Marker_key = h._Marker_key)
order by m.category, m.symbol
go

