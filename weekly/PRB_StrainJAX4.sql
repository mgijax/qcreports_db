
set nocount on
go

print ''
print 'New JR#s created in past week'
print ''

set nocount off
go

select a.accID
from ACC_Accession a
where a._MGIType_key = 10
and a._LogicalDB_key = 22
and a.creation_date between dateadd(day, -7, getdate()) and getdate()
order by a.accID
go

