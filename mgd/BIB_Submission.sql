set nocount on
go

select _Refs_key, jnum, _primary, title, short_citation, authors, year
into #submission
from BIB_All_View
where journal = 'Submission'
go

set nocount off
go

print ""
print "RUN #1 - Potential Submission References Matches to non-Submission References"
print ""

select MGD = b.jnum, substring(b.short_citation,1,50),
Submission = s.jnum, substring(s.title,1,40)
from BIB_All_View b, #submission s
where b._Refs_key != s._Refs_key
and b.journal != 'Submission'
and b._primary = s._primary
and b.year >= s.year
go

print ""
print "RUN #2 - Potential Submission References Matches to non-Submission References"
print ""

select MGD = b.jnum, substring(b.short_citation,1,50),
Submission = s.jnum, substring(s.title,1,40)
from BIB_All_View b, #submission s
where b._Refs_key != s._Refs_key
and b.journal != 'Submission'
and b.year >= s.year
and substring(b.title,1,25) = substring(s.title,1,25)
go

