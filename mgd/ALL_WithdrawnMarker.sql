
\echo ''
\echo 'Alleles with Withdrawn Markers'
\echo ''

select m.symbol, a.symbol, t.term, a.isWildType
from all_allele a, mrk_marker m, voc_term t
where a._marker_key = m._marker_key
and m._marker_status_key = 2 
and a._allele_status_key = t._term_key
order by a.iswildtype, m.symbol
;

