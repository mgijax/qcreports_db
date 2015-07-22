\echo ''
\echo 'Cell Lines'
\echo ''

select distinct term
from VOC_Term where _Vocab_key = 18
order by term
;

