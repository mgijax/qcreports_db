print ""
print "Cell Lines"
print ""

select distinct cellLine from PRB_Source
order by cellLine
go

