set nocount on
go

select distinct s._Strain_key, substring(s.strain,1,85) as strain, 
sm.symbol, sm._Marker_key, sm._Allele_key
into #strains
from PRB_Strain s, PRB_Strain_Attribute_View st, PRB_Strain_Marker_View sm
where s.strain like '%>'
and s._Strain_key = st._Strain_key
and st.term in ('mutant stock', 'mutant strain', 'targeted mutation')
and s._Strain_key = sm._Strain_key
go

select _Strain_key
into #multiples
from #strains
group by _Strain_key having count(*) > 1
go

set nocount off
go

print ''
print 'Strains ending with ''>'''
print 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
print 'with Multiple Markers and at least one Marker has no Alleles'
print ''

select distinct s.strain, s.symbol
from #multiples m, #strains s
where m._Strain_key = s._Strain_key
and s._Allele_key is null
order by s.strain
go

