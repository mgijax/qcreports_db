set nocount on
go

select distinct s._Strain_key, strain = substring(s.strain,1,85),
alleleSymbol = substring(strain, charindex("-", strain) + 1, char_length(s.strain)),
sm.symbol, sm._Marker_key, sm._Allele_key
into #strains
from PRB_Strain s, PRB_Strain_Marker_View sm
where s.strain like '%<%>%'
and s._Strain_key = sm._Strain_key
go

set nocount off
go

print ""
print "Strains containing '<>' "
print "with any number of Markers and Marker has no Allele"
print "and Allele symbol embedded in Strain is in MGD"
print ""

select s.strain, s.symbol, alleleSymbol = substring(s.alleleSymbol, 1, 35)
from #strains s
where s._Allele_key is null
and exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
go

