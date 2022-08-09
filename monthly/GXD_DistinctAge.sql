
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
from gxd_gellane, voc_term t
where _gelcontrol_key = t._term_key and t.term = 'No'
order by age;

