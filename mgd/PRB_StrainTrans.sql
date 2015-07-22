\echo ''
\echo 'Strains - Transgenic or Targeted Mutation'
\echo ''

select a.accID as jr, substring(t.term,1,30) as straintype, 
substring(s.strain,1,125) as strain
from PRB_Strain s, PRB_Strain_Attribute_View t, ACC_Accession a
where s._Strain_key = t._Strain_key
and t.term in ('transgenic', 'targeted mutation')
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
order by s.strain
;

