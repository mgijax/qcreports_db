set nocount on
go

select distinct s._Strain_key, substring(s.strain,1,50) as strain, s.private,
substring(strain, charindex('-', strain) + 1, char_length(s.strain)) as alleleSymbol,
sm.symbol, sm._Marker_key, sm._Allele_key
into #strains
from PRB_Strain s, PRB_Strain_Attribute_View st, PRB_Strain_Marker_View sm
where s.strain like '%>'
and s.strain not like 'STOCK%'
and s._Strain_key = st._Strain_key
and st.term in ('mutant stock', 'mutant strain', 'targeted mutation')
and s._Strain_key = sm._Strain_key
go

select _Strain_key
into #singles
from #strains
group by _Strain_key having count(*) = 1
go

set nocount off
go

print ''
print 'Private Strains ending with '>' '
print 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
print 'with at most one Marker and Marker has no Allele'
print 'and Allele symbol is *not* in MGD'
print ''

select substring(l.name, 1, 20) as externalDB, a.accID, s.strain, s.symbol, 
substring(s.alleleSymbol, 1, 35) as alleleSymbol
from #singles ss, #strains s, ACC_Accession a, ACC_LogicalDB l
where ss._Strain_key = s._Strain_key
and s._Allele_key is null
and s.private = 1
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
and not exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
go

print ''
print 'Public Strains ending with '>' '
print 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
print 'with at most one Marker and Marker has no Allele'
print 'and Allele symbol is *not* in MGD'
print ''

select substring(l.name, 1, 20) as externalDB, a.accID, s.strain, s.symbol, 
substring(s.alleleSymbol, 1, 35) as alleleSymbol
from #singles ss, #strains s, ACC_Accession a, ACC_LogicalDB l
where ss._Strain_key = s._Strain_key
and s._Allele_key is null
and s.private = 0
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
and not exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
go

