print ""
print "References Which Need NLM Updates"
print "in Medline query format:"
print ""
print "'first author' [AU] AND 'year' [YR] AND 'journal name' [TA]"
print ""

select "'" + r._primary + "' [AU] AND '"  + convert(char(4), r.year) + "' [YR] AND '" + r.journal + "' [TA]"
from BIB_Refs r
where NLMstatus = 'Y'
and not exists
(select a._Accession_key from BIB_Acc_View a
where a._Object_key = r._Refs_key
and a._LogicalDB_key = 29)
order by r.year, r._primary
go

