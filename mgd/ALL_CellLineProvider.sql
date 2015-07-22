
print ''
print 'Cases where the cell line creator has been entered'
print 'but the Accession ID of the mutant cell line has not been attached.'
print '(See the EI Mutant Cell Line Module)'
print ''

select substring(ac.creator,1,25) as creator, acc.accID, 
substring(a.symbol,1,35) as symbol, 
substring(ac.cellLine,1,25) as "mutant cell line ID"
from ALL_Allele a, ALL_Allele_CellLine c, ALL_CellLine_View ac, ACC_Accession acc
where a._Allele_key = c._Allele_key
and c._MutantCellLine_key = ac._CellLine_key
and ac.creator is not null
and ac.creator != 'Not Specified'
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and not exists (select 1 from ACC_Accession aa
where aa._MGIType_key = 28
and c._MutantCellLine_key = aa._Object_key)
order by ac.creator
go

/*
 * since some celllines have > 1 accession id and one of them may be correct...
 * select all cell lines that contain a cellline != accession id
 * remove those that also contain a cellline == accession id
*/

select c._Allele_key, aa.accID
into #notexists
from ALL_Allele_CellLine c, ALL_CellLine ac, ACC_Accession aa
where c._MutantCellLine_key = ac._CellLine_key
and aa._MGIType_key = 28
and ac._CellLine_key = aa._Object_key
and ac.cellLine != aa.accID
and not exists (select 1 from ALL_Allele_CellLine c2, ALL_CellLine ac2, ACC_Accession aa2
	where c2._allele_key = c._allele_key
		and c2._mutantcellline_key = ac2._cellline_key
		and aa2._object_key = ac2._cellline_key
		and aa2._mgitype_key = 28
		and aa2.accID = ac2.cellline)
go

create index idx_allele on #notexists(_Allele_key)
go

print ''
print 'Cases where the cell line creator has been entered'
print 'and the Accession ID of the mutant cell line has been attached,'
print 'but the mutant cell line name is not the same as the name of the Accession ID.'
print '(See the EI Mutant Cell Line Module)'
print ''

select substring(ac.creator,1,25) as creator, acc.accID, 
substring(a.symbol,1,35) as symbol, 
substring(ac.cellLine,1,25) as "mutant cell line ID", e.accID "accession id"
from ALL_Allele a, ALL_Allele_CellLine c, ALL_CellLine_View ac, ACC_Accession acc, #notexists e
where a._Allele_key = c._Allele_key
and c._MutantCellLine_key = ac._CellLine_key
and ac.creator is not null
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and a._Allele_key = e._Allele_key
order by ac.creator
go

