print ""
print "References In Press/Submissions"
print ""

select jnum, substring(short_citation, 1, 75)
from BIB_All_View
where vol like '%in press%' 
or pgs like '%in press%'
or journal = 'Submission'
order by year, _primary
go
