\echo ''
\echo 'Markers which contain Alleles which do not match the Marker Symbol'
\echo ''

select m.symbol as "Marker", a.symbol as "Allele"
from ALL_Allele a, MRK_Marker m
where a._Marker_key = m._Marker_key
and m._Organism_key = 1
and a.symbol != '+'
and m.symbol not in ('a', 'A')
and a.symbol not like '%' || m.symbol || '%'
and m._Marker_Status_key in (1,2)
;

/* duplicate alleles by symbol */
select symbol
INTO TEMPORARY TABLE duplicates
from ALL_Allele
where symbol != '+'
group by symbol having count(*) > 1
;

create index dups_idx1 on duplicates(symbol)
;

\echo ''
\echo 'Duplicate Allele Symbols'
\echo ''

select a.symbol, a.markerSymbol
from duplicates d, ALL_Allele_View a
where d.symbol = a.symbol
and a.symbol not in ('a', 'A')
order by creation_date desc
;

\echo ''
\echo 'Approved Transgenes where :'
\echo '    the marker name and the allele name are not identical'
\echo '    or'
\echo '    the marker symbol and the allele symbol are not identical'
\echo ''

select m.symbol as "Marker Symbol", substring(m.name,1,60) as "Marker Name", 
       a.symbol as "Allele Symbol", substring(a.name,1,60) as "Allele Name"
from ALL_Allele a, MRK_Marker m
where a._Allele_Status_key = 847114
and a._Marker_key = m._Marker_key
and m._Marker_Type_key = 12
and (a.symbol != m.symbol or a.name != m.name)
order by m.symbol
;

