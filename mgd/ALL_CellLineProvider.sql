
set nocount on
go

print ""
print "Cases where the ES cell line provider has been entered"
print "but the Accession ID of the mutant ES cell line has not been attached."
print "(See the EI ESCellLineModule)"
print ""

select substring(c.provider,1,25) "provider", acc.accID, 
substring(a.symbol,1,35) "symbol", 
substring(c.cellLine,1,25) "mutant ES cell line ID"
from ALL_Allele a, ALL_CellLine c, ACC_Accession acc
where a._MutantESCellLine_key = c._CellLine_key
and c.provider is not null
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and not exists (select 1 from ACC_Accession aa
where aa._MGIType_key = 28
and c._CellLine_key = aa._Object_key)
order by c.provider
go

print ""
print "Cases where the ES cell line provider has been entered"
print "and the Accession ID of the mutant ES cell line has been attached,"
print "but the mutant ES cell line ID is not the same as the name of the Accession ID."
print "(See the EI ESCellLineModule)"
print ""

select substring(c.provider,1,25) "provider", acc.accID, 
substring(a.symbol,1,35) "symbol", 
substring(c.cellLine,1,25) "mutant ES cell line ID", aa.accID "accession id"
from ALL_Allele a, ALL_CellLine c, ACC_Accession acc, ACC_Accession aa
where a._MutantESCellLine_key = c._CellLine_key
and c.provider is not null
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and aa._MGIType_key = 28
and c._CellLine_key = aa._Object_key
and c.cellLine != aa.accID
order by c.provider
go

