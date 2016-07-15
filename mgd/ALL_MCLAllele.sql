
select a._MutantCellLine_key
INTO TEMPORARY TABLE mutant
from ALL_Allele_Cellline a
group by a._MutantCellLine_key having count(*) > 1
;

\echo ''
\echo 'MCL''s that are associated with more than one Allele'
\echo ''

select substring(c.cellLine,1,50) as cellLine, 
       substring(aa.symbol,1,50) as symbol, aa.modification_date
from mutant m, ALL_Allele_CellLine a, ALL_Allele aa, ALL_CellLine c
where m._MutantCellLine_key = a._MutantCellLine_key
and a._Allele_key = aa._Allele_key
and m._MutantCellLine_key = c._CellLine_key
order by aa.modification_date desc, c.cellLine
;

