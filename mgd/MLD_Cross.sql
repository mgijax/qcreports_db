print ""
print "Mapping Cross - 2 Point Data In Matrix Format"
print ""

select distinct r.jnum, substring(r.short_citation, 1, 50), exptType = substring(r.exptType, 1, 30), r.tag
from MLD_Expt_View r, MLD_MCDataList m
where m.alleleLine = 'parental'
and m._Expt_key = r._Expt_key
order by r.short_citation
go

print ""
print "Mapping Cross - Having Neither Matrix nor 2 Point Data"
print ""

select distinct r.jnum, substring(r.short_citation, 1, 50), exptType = substring(r.exptType, 1, 30), r.tag
from MLD_Expt_View r, MLD_Matrix m
where not exists (select d.* from MLD_MCDataList d where m._Expt_key = d._Expt_key)
and not exists (select p.* from MLD_MC2point p where m._Expt_key = p._Expt_key)
and m._Expt_key = r._Expt_key
order by r.short_citation
go

print ""
print "Mapping Cross - Missing Allele Line in Matrix"
print ""
 
select distinct r.jnum, substring(r.short_citation, 1, 50), exptType = substring(r.exptType, 1, 30), r.tag
from MLD_Expt_View r, MLD_MCDataList m
where m.alleleLine is null
and m._Expt_key = r._Expt_key
order by r.short_citation
go
  
