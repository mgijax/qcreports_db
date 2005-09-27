set nocount on
go

select s._Strain_key, strain = substring(s.strain,1,85)
into #strains
from PRB_Strain s
where s.private = 1
go

create index idx1 on #strains(_Strain_key)
go

select s.strain, ps._Source_key
into #sequencesource
from #strains s, PRB_Source ps
where s._Strain_key = ps._Strain_key
go

create index idx1 on #sequencesource(_Source_key)
go

select s.strain, ss._Sequence_key
into #sequence
from #sequencesource s, SEQ_Source_Assoc ss
where s._Source_key = ss._Source_key
go

create index idx1 on #sequence(_Sequence_key)
go

set nocount off
go

print ""
print "Private Strains Referenced by other Database Objects"
print ""

select a.accID, s.strain, mgiObject = 'Sequence'
from #sequence s, ACC_Accession a
where s._Sequence_key = a._Object_key
and a._MGIType_key = 19
and a.preferred = 1
union
select a.accID, s.strain, mgiObject = 'Genotype'
from #strains s, GXD_Genotype g, ACC_Accession a
where s._Strain_key = g._Strain_key
and g._Genotype_key = a._Object_key
and a._MGIType_key = 12
and a._LogicalDB_key = 1
and a.prefixPart = "MGI:"
and a.preferred = 1
order by s.strain
go

