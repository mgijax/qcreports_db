set nocount on
go

select _Strain_key, strain
into #strains
from PRB_Strain
group by strain having count(*) > 1

set nocount off
go

print ""
print "Duplicate Strains"
print ""

select jr = null, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from #strains s, strains..MLP_StrainTypes_View t
where s.strain not like '%)F1%'
and s._Strain_key = t._Strain_key
and not exists (select 1 from PRB_Strain_Acc_View a
where a._Object_key = s._Strain_key
and a._LogicalDB_key = 22)
union
select jr = a.accID, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from #strains s, strains..MLP_StrainTypes_View t, PRB_Strain_Acc_View a
where s.strain not like '%)F1%'
and s._Strain_key = t._Strain_key
and a._Object_key = s._Strain_key
and a._LogicalDB_key = 22
order by s.strain
go

