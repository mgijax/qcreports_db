
\echo ''
\echo 'InSitu Distinct Age, AgeMin, AgeMax'
\echo ''

select distinct age, agemin, agemax 
from gxd_specimen
order by age;

\echo ''
\echo 'Gel Lane Distinct Age, AgeMin, AgeMax'
\echo ''

select distinct age, agemin, agemax 
from gxd_gellane
where _gelcontrol_key = 1
order by age;

