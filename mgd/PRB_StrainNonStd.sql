print ""
print "Non Standard Strains (excluding F1 and F2)"
print ""

select jr = null, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, MLP_StrainTypes_View t
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key *= t._Strain_key
and not exists (select 1 from PRB_Strain_Acc_View a
where a._Object_key = s._Strain_key
and a._LogicalDB_key = 22)
union
select jr = a.accID, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, MLP_StrainTypes_View t, PRB_Strain_Acc_View a
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key *= t._Strain_key
and a._Object_key = s._Strain_key
and a._LogicalDB_key = 22
order by s.strain
go

