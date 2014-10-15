
/* papers selected for Mapping in the past week */

set nocount on

select r._Refs_key, r.creation_date
into #triage
from BIB_Refs r, BIB_DataSet_Assoc a
where r.creation_date between dateadd(day, -7, getdate()) and dateadd(day, -1, getdate())
and r._Refs_key = a._Refs_key
and a._DataSet_key = 1001

go

create index idx1 on #triage(_Refs_key)

go

print ''
print 'Papers Selected For Mapping in the past week'
print ''

set nocount off

select v.jnumID, substring(v.short_citation, 1, 50) as short_citation
from #triage t, BIB_All_View v
where t._Refs_key = v._Refs_key
order by v.jnum
go

