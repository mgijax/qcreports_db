set nocount on
go

select distinct e._Refs_key, exptType = substring(e.exptType, 1, 30), e.tag
into #expts
from MLD_Expts e, MLD_MC2point m
where m.numParentals < m.numRecombinants
and m._Expt_key = e._Expt_key
go

set nocount off
go

print ""
print "Mapping - Cross - Recombinants > Parentals"
print ""

select b.jnum, substring(b.short_citation, 1, 50), exptType = substring(e.exptType, 1, 30), e.tag
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

set nocount on
go

drop table #expts
go

select distinct e._Refs_key, exptType = substring(e.exptType, 1, 30), e.tag
into #expts
from MLD_Expts e, MLD_RI2point m
where m.numTotal < m.numRecombinants
and m._Expt_key = e._Expt_key
go

set nocount off
go

print ""
print "Mapping - RI - Recombinants > Total"
print ""

select b.jnum, substring(b.short_citation, 1, 50), exptType = substring(e.exptType, 1, 30), e.tag
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

