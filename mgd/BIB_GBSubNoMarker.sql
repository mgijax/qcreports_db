print ""
print "GenBank Submission References with no Marker associations"
print ""

select b.jnum
from BIB_All_View b
where b.journal = 'GenBank Submission'
and not exists (select 1 from MRK_Reference r
where b._Refs_key = r._Refs_key)
order by jnum
go
