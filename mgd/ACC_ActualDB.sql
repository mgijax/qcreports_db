
print ""
print "ACC Actual DB"
print ""

select a._LogicalDB_key, l.name, a._ActualDB_Key, a.name, a.url
from ACC_ActualDB a, ACC_LogicalDB l
where l._LogicalDB_key = a._LogicalDB_key
order by l.name
go


