set nocount on
go

select ecount = count(_Annot_key), _EvidenceTerm_key
into #stats
from VOC_Evidence
group by _EvidenceTerm_key
go

set nocount off
go

print ""
print "Total # of Annotations by GO Evidence Code"
print ""

select s.ecount "#", t.abbreviation "Evidence Code"
from #stats s, VOC_Term t
where s._EvidenceTerm_key = t._Term_key
go

