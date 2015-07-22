
/* papers selected for Expression in the past week */

select r._Refs_key, r.creation_date
into #triageA
from BIB_Refs r, BIB_DataSet_Assoc a
where a.creation_date between dateadd(day, -7, getdate()) and dateadd(day, -1, getdate())
and r._Refs_key = a._Refs_key
and a._DataSet_key = 1004

go

create index idx1 on #triageA(_Refs_key)

go

\echo ''
\echo 'Papers Selected For Expression in past week '
\echo 'by Data Set creation date'
\echo ''

select v.jnumID, substring(v.short_citation, 1, 50) as short_citation
from #triageA t, BIB_All_View v
where t._Refs_key = v._Refs_key
order by v.jnum
go

