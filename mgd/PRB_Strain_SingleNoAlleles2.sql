set nocount on
go

select distinct s._Strain_key, strain = substring(s.strain,1,85), s.private,
alleleSymbol = substring(strain, charindex("-", strain) + 1, char_length(s.strain)),
sm.symbol, sm._Marker_key, sm._Allele_key
into #strains
from PRB_Strain s, MLP_StrainTypes st, MLP_StrainType t, PRB_Strain_Marker_View sm
where s.strain like '%>'
and s.strain not like 'STOCK%'
and s._Strain_key = st._Strain_key
and st._StrainType_key = t._StrainType_key
and t.strainType in ('mutant stock', 'mutant strain', 'targeted mutation')
and s._Strain_key = sm._Strain_key
go

select *
into #singles
from #strains
group by _Strain_key having count(*) = 1
go

set nocount off
go

print ""
print "Strains ending with '>' "
print "with Strain Type of mutant stock, mutant strain or targeted mutation "
print "with at most one Marker and Marker has no Allele"
print "and Allele symbol is *not* in MGD"
print ""

select s.strain, s.private, s.symbol, alleleSymbol = substring(s.alleleSymbol, 1, 35)
from #singles s
where s._Allele_key is null
and not exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
go

