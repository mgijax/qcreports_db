print ""
print "Strains - Transgenic or Targeted Mutation"
print ""

select jr = a.accID, substring(t.strainType,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, MLP_StrainTypes_View t, PRB_Strain_Acc_View a
where s._Strain_key = t._Strain_key
and t.strainType in ('transgenic', 'targeted mutation')
and a._Object_key = s._Strain_key
and a._LogicalDB_key = 22
order by s.strain
go

