print ""
print "Strains containing F1 and F2"
print ""

select s.standard, jr = null, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, strains..MLP_StrainTypes_View t
where (s.strain like '%)F1%' or s.strain like '%)F2%')
and s._Strain_key = t._Strain_key
and not exists (select 1 from PRB_Strain_Acc_View a
where a._Object_key = s._Strain_key
and a._LogicalDB_key = 22)
union
select s.standard, jr = a.accID, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, strains..MLP_StrainTypes_View t, PRB_Strain_Acc_View a
where (s.strain like '%)F1%' or s.strain like '%)F2%')
and s._Strain_key = t._Strain_key
and a._Object_key = s._Strain_key
and a._LogicalDB_key = 22
order by s.standard desc, s.strain
go

