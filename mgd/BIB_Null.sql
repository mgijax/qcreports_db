print ""
print "References With NULL Author/Journal/Vol/Page/Year"
print ""

select jnum, substring(short_citation, 1, 75)
from BIB_All_View
where journal != "Submission"
and (_primary is null
or journal is null
or vol is null
or pgs is null
or year is null)
order by year, _primary
go

