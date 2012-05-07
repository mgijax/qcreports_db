begin;

print ''
print 'Markers which contain Alleles which do not match the Marker Symbol'
print ''

select m.symbol as "Marker", a.symbol as "Allele"
from ALL_Allele a, MRK_Marker m
where a._Marker_key = m._Marker_key
and a.symbol != '+'
and a.symbol not like '%' || m.symbol || '%'
go

set nocount on
go

/* duplicate alleles by symbol */
select symbol
into #duplicates1
from ALL_Allele
where symbol != '+'
group by symbol having count(*) > 1
go

create index dups_idx1 on #duplicates1(symbol)
go

select a._Allele_key, a.symbol
into #duplicates
from ALL_Allele a, #duplicates1 d
where d.symbol = a.symbol
go

set nocount off
go

print ''
print 'Duplicate Allele Symbols'
print ''

select a.symbol, a.markerSymbol
from #duplicates d, ALL_Allele_View a
where d._Allele_key = a._Allele_key
order by creation_date desc
go

print ''
print 'Approved Transgenes where :'
print '    the marker name and the allele name are not identical'
print '    or'
print '    the marker symbol and the allele symbol are not identical'
print ''

select m.symbol as "Marker Symbol", substring(m.name,1,60) as "Marker Name", 
       a.symbol as "Allele Symbol", substring(a.name,1,60) as "Allele Name"
from ALL_Allele a, ALL_Marker_Assoc am, MRK_Marker m
where a._Allele_Status_key = 847114
and a._Allele_key = am._Allele_key
and am._Marker_key = m._Marker_key
and m._Marker_Type_key = 12
and (a.symbol != m.symbol or a.name != m.name)
order by m.symbol
go

commit;

drop table duplicates1
go
drop table duplicates
go

