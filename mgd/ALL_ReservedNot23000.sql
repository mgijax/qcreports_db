print ""
print "Reserved Alleles w/ Primary Reference != J:23000"
print ""

select a.symbol, r.jnumID
from ALL_Allele a, ALL_Reference_View r
where a._Allele_Status_key = 3
and a._Allele_key = r._Allele_key
and r._RefsType_key = 1
and r._Refs_key != 22864
order by a.symbol
go

