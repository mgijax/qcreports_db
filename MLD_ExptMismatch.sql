print ""
print "Non-CROSS Experiments with data in CROSS Experiment Tables"
print ""

select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_Matrix m 
where e.exptType != "CROSS" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_MC2point m 
where e.exptType != "CROSS" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_MCDataList m 
where e.exptType != "CROSS" and e._Expt_key = m._Expt_key
order by e._Expt_key
go

print ""
print "Non-FISH Experiments with data in FISH Experiment Tables"
print ""

select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_FISH m
where e.exptType != "FISH" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_FISH_Region m 
where e.exptType != "FISH" and e._Expt_key = m._Expt_key
order by e._Expt_key
go

print ""
print "Non-HYBRID Experiments with data in HYBRID Experiment Tables"
print ""

select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_Hybrid m
where e.exptType != "HYBRID" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_Concordance m
where e.exptType != "HYBRID" and e._Expt_key = m._Expt_key
order by e._Expt_key
go

print ""
print "Non-INSITU Experiments with data in INSITU Experiment Tables"
print ""

select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_InSitu m
where e.exptType != "IN SITU" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_ISRegion m
where e.exptType != "IN SITU" and e._Expt_key = m._Expt_key
order by e._Expt_key
go

print ""
print "Non-RI Experiments with data in RI Experiment Tables"
print ""

select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_RI m
where e.exptType != "RI" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_RI2Point m
where e.exptType != "RI" and e._Expt_key = m._Expt_key
union
select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_RIData m
where e.exptType != "RI" and e._Expt_key = m._Expt_key
order by e._Expt_key
go

print ""
print "Non-CONTIG Experiments with data in CONTIG Experiment Tables"
print ""

select e._Expt_key, e._Refs_key, substring(e.exptType,1,30), e.tag
from MLD_Expts e, MLD_Contig m
where e.exptType != "CONTIG" and e._Expt_key = m._Expt_key
order by e._Expt_key
go

