print ''
print 'Strains containing F1 and F2'
print ''

(
select s.standard, null as jr, substring(t.term,1,30) as straintype, 
substring(s.strain,1,125) as strain
from PRB_Strain s 
     LEFT OUTER JOIN PRB_Strain_Attribute_View t on (s._Strain_key = t._Strain_key)
where (s.strain like '%)F1%' or s.strain like '%)F2%')
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
union
select s.standard, a.accID as jr, substring(t.term,1,30) as straintype, 
substring(s.strain,1,125) as strain
from PRB_Strain s
     LEFT OUTER JOIN PRB_Strain_Attribute_View t on (s._Strain_key = t._Strain_key),
     ACC_Accession a
where (s.strain like '%)F1%' or s.strain like '%)F2%')
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
)
order by standard desc, strain
go

