select strain
into #strains
from PRB_Strain
group by strain having count(*) > 1

\echo ''
\echo 'Duplicate Strains'
\echo ''

(
select null as jr, 
substring(t.term,1,30) as straintype, 
substring(s.strain,1,125) as strain
from #strains s,
     PRB_Strain ss
     	LEFT OUTER JOIN PRB_Strain_Attribute_View t on (ss._Strain_key = t._Strain_key)
where s.strain not like '%)F1%'
and s.strain = ss.strain
and not exists (select 1 from ACC_Accession a
where ss._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
union
select a.accID as jr, 
substring(t.term,1,30) as straintype, 
substring(s.strain,1,125) as strain
from #strains s,
     PRB_Strain ss
     	LEFT OUTER JOIN PRB_Strain_Attribute_View t on (ss._Strain_key = t._Strain_key), 
     ACC_Accession a
where s.strain not like '%)F1%'
and s.strain = ss.strain
and ss._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
)
order by strain
go

