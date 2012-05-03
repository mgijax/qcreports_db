set nocount on
go

select m._Marker_key, m.symbol, category = 'a'
into #markers
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and (m.symbol like '[A-Z][0-9][0-9][0-9][0-9][0-9]' 
or m.symbol like '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]')
union
select m._Marker_key, m.symbol, category = 'b'
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m.symbol like '%Rik'
and m.name like 'RIKEN%'
union
select m._Marker_key, m.symbol, category = 'c'
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m.name like 'DNA segment%'
go

create index idx1 on #markers(_Marker_key)
go

select m.*
into #sequences1
from #markers m
where exists (select 1 from ACC_Accession a, ACC_AccessionReference r
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 9
and a._Accession_key = r._Accession_key
and r._Refs_key = 64047)
go

create index idx1 on #sequences1(_Marker_key)
go

/* find pubmed ids by EntrezGene ID */
/* exclude certain pubmed ids */

select s.*
into #sequencesFinal
from #sequences1 s
where exists (select 1 from ACC_Accession a, radar..DP_EntrezGene_PubMed c
where s._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 55
and a.accID = c.geneID)
union
select s.*
from #sequences1 s
where exists (select 1 from ACC_Accession a 
where s._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 55
and not exists (select 1 from radar..DP_EntrezGene_PubMed c
where a.accID = c.geneID))
go

create index idx1 on #sequencesFinal(_Marker_key)
go

set nocount off
go

print ''
print 'MGI Markers with Uninformative Nomenclature'
print 'where symbol is:'
print '   a) GenBank Accession ID'
print '   b) RIKEN symbol'
print '   c) DNA segment'
print 'where symbol has acquired a Sequence Accession ID from EntrezGene'
print 'where symbol has no homology entry in MGI'
print ''

select m.symbol, m.category
from #sequencesFinal m
where not exists (select 1 from HMD_Homology_Marker h where m._Marker_key = h._Marker_key)
order by m.category, m.symbol
go

drop table #markers
go
drop table #sequences1
go
drop table #sequencesFinal
go

