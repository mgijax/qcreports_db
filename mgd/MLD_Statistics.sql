set nocount on
go

select distinct e._Refs_key, e.exptType, e.tag, e._Expt_key
into #expts 
from MLD_Expts e, MLD_Matrix m, CRS_Cross c, MLD_Statistics s
where e._Expt_key = m._Expt_key
and m._Cross_key = c._Cross_key
and c.type like '1%'
and m._Expt_key = s._Expt_key
and s.pcntrecomb > 50
go

set nocount off
go

print ""
print "Mapping Cross - Statistics w/ Pct Recombination > 50"
print ""

select b.jnum, substring(b.short_citation, 1, 50), exptType = substring(e.exptType, 1, 30), 
e.tag, e._Expt_key
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

set nocount on
go

drop table #expts
go

select distinct e._Refs_key, e.exptType, e.tag, e._Expt_key
into #expts
from MLD_Expts e, MLD_Matrix_View m
where e._Expt_key = m._Expt_key
and (m.type = '1' or m.type like '1[12]')
and not exists (select s._Expt_key from MLD_Statistics s where m._Expt_key = s._Expt_key)
go

set nocount off
go

print ""
print "Mapping Cross - Missing Statistics"
print ""

select b.jnum, substring(b.short_citation, 1, 50), exptType = substring(e.exptType, 1, 30), 
e.tag, e._Expt_key
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

set nocount on
go

drop table #expts
go

select distinct r._Expt_key
into #ris
from MLD_RIData r
group by r._Expt_key
having count(*) > 1
go

select distinct e._Refs_key, e.exptType, e.tag, e._Expt_key
into #expts
from #ris r, MLD_Expts e
where r._Expt_key = e._Expt_key
and not exists (select s._Expt_key from MLD_Statistics s where e._Expt_key = s._Expt_key)
go

set nocount off
go

print ""
print "Mapping RI - Missing Statistics"
print ""

select b.jnum, substring(b.short_citation, 1, 50), exptType = substring(e.exptType, 1, 30), 
e.tag, e._Expt_key
from #expts e, BIB_All_View b
where e._Refs_key = b._Refs_key
order by b.short_citation
go

drop table #expts
go

