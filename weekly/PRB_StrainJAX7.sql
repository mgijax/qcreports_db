
set nocount on
go

print ''
print 'New MMRRC JR#s created in past week'
print ''

set nocount off
go

select a.accID
from ACC_Accession a, PRB_Strain s
where a._MGIType_key = 10
and a._LogicalDB_key = 38
and a.creation_date between dateadd(day, -7, getdate()) and getdate()
and a._Object_key = s._Strain_key
order by a.accID
go

