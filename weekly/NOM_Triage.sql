
/* papers for Nomenclature in the past week */

set nocount on

declare @cdate char(10)
declare @bdate char(10)
declare @edate char(10)

select @cdate = convert(char(10), getdate(), 101)
select @bdate = convert(char(10), dateadd(day, -7, @cdate), 101)
select @edate = convert(char(10), dateadd(day, 1, @cdate), 101)

select r._Refs_key, r.creation_date
into #triage
from BIB_Refs r, BIB_DataSet_Assoc a
where r.creation_date between @bdate and @edate
and r._Refs_key = a._Refs_key
and a._DataSet_key = 1006

create index idx1 on #triage(_Refs_key)

print ""
print "Papers Selected For Nomenclature from %1! to %2!", @bdate, @edate
print ""

set nocount off

select jnum = a1.accID, t.creation_date, pubmed = a2.accID
from #triage t, ACC_Accession a1, ACC_Accession a2
where t._Refs_key = a1._Object_key
and a1._MGIType_key = 1
and a1._LogicalDB_Key = 1
and a1.prefixPart = "J:"
and a1._Object_key *= a2._Object_key
and a2._LogicalDB_Key = 29
order by a1.numericPart
go

