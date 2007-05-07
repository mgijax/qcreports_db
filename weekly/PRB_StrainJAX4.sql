
set nocount on
go

declare @printDate varchar(255)
select @printDate = "New JR#s created between " + 
	convert(char(10), dateadd(day, -7, getdate()), 101) + 
	" and " + convert(char(10), getdate(), 101)

print ""
print @printDate
print ""

set nocount off
go

select a.accID
from ACC_Accession a
where a._MGIType_key = 10
and a._LogicalDB_key = 22
and a.creation_date between dateadd(day, -7, getdate()) and getdate()
order by a.accID
go

quit

END

