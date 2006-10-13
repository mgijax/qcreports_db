
/* papers selected for Expression in the past week */

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
and a._DataSet_key = 1004

create index idx1 on #triage(_Refs_key)

print ""
print "Papers Selected For Expression from %1! to %2!", @bdate, @edate
print ""

set nocount off

select v.jnumID, substring(v.short_citation, 1, 50)
from #triage t, BIB_All_View v
where t._Refs_key = v._Refs_key
order by v.jnum
go

