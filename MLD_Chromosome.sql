set nocount on
go

select distinct _Refs_key, exptType, tag, chromosome
into #expts
from MLD_Expts
where 
not chromosome like '[123456789]'
and not chromosome like '1[0123456789]'
and not chromosome like '[XY]'
and not chromosome = 'XY'
and not chromosome = 'UN'
go

set nocount off
go

print ""
print "Mapping - Experiment Invalid Chromosome"
print ""

select b.jnum, substring(b.short_citation, 1, 25), exptType = substring(e.exptType, 1, 30), e.tag, 
e.chromosome
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

set nocount on
go

drop table #expts
go

select distinct e.exptType, e._Refs_key, echr = e.chromosome, mchr = m.chromosome, m.symbol
into #expts
from MLD_Expts e, MLD_Expt_Marker g, MRK_Marker m
where e._Expt_key = g._Expt_key
and g._Marker_key = m._Marker_key
and e.chromosome != m.chromosome
go

set nocount off
go

print ""
print "Mapping - Experiment Invalid Chromosome Vs. Marker List Chromosome"
print ""

select exptType = substring(e.exptType, 1, 30), b.jnum, substring(b.short_citation, 1, 25),
e.echr "Mapping Chr", e.symbol, e.mchr "Marker Chr"
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by e.exptType, b.short_citation
go

set nocount on
go

drop table #expts
go

select distinct e._Refs_key, e.exptType, e.tag, c.chromosome
into #expts
from MLD_Expts e, MLD_Hybrid h, MLD_Concordance c
where 
h.chrsOrGenes = 0
and h._Expt_key = c._Expt_key
and not c.chromosome like '[1-9]'
and not c.chromosome like '[12][0-9]'
and not c.chromosome like '[XY]'
and not c.chromosome = 'XY'
and c._Expt_key = e._Expt_key
go

set nocount off
go

print ""
print "Mapping - Hybrid Invalid Chromosome"
print ""

select b.jnum, substring(b.short_citation, 1, 25), exptType = substring(e.exptType, 1, 30), e.tag, 
e.chromosome
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

set nocount on
go

drop table #expts
go

select distinct e._Refs_key, e.exptType, e.tag, c.chromosome
into #expts
from MLD_Expts e, MLD_Hybrid h, MLD_Concordance c
where 
h.chrsOrGenes = 0
and h._Expt_key = c._Expt_key
and c.chromosome like '[A-W]%'
and c._Expt_key = e._Expt_key
go

set nocount off
go

print ""
print "Mapping - Hybrid Invalid Marker/Chromosome Flag"
print ""

select b.jnum, substring(b.short_citation, 1, 25), exptType = substring(e.exptType, 1, 30), e.tag, 
e.chromosome
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

drop table #expts
go

