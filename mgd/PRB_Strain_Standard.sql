
\echo ''
\echo '''STOCK'' or ''semicolon'' strains marked standard'
\echo ''

select s.strain
from PRB_Strain s
where s.standard = 1
and (s.strain like 'STOCK%'
or (s.strain like '%;%' and s.strain not like '%T(%;%)%'))
;

