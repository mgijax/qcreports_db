print ""
print "Strains containing F1 and F2"
print ""

select s.standard, jr = null, substring(t.term,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, PRB_Strain_Type_View t
where (s.strain like '%)F1%' or s.strain like '%)F2%')
and s._Strain_key *= t._Strain_key
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
union
select s.standard, jr = a.accID, substring(t.term,1,30) "straintype", substring(s.strain,1,125) "strain"
from PRB_Strain s, PRB_Strain_Type_View t, ACC_Accession a
where (s.strain like '%)F1%' or s.strain like '%)F2%')
and s._Strain_key *= t._Strain_key
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
order by s.standard desc, s.strain
go

