
\echo ''
\echo 'MGI gene symbols that have changed and with Noctua GO annotations'
\echo ''

select distinct h._marker_key, m1.symbol as currentSymbol, h._history_key, mhist.symbol as oldSymbol, a1.accid as currentID, t.term as event, CAST(h.event_date AS DATE) as eventDate 
into temporary table changed
from voc_annot va, voc_evidence ve, mgi_user u, mrk_marker m1, mrk_history h, mrk_marker mhist, voc_term t, acc_accession a1
where va._annottype_key = 1000
and va._annot_key = ve._annot_key
and ve._createdby_key= u._user_key
and u.login like 'NOCTUA%'
and va._object_key = m1._marker_key
and va._object_key = h._marker_key
and h._marker_event_key in (106563607, 106563605, 106563606) -- allele of, rename, merged
and h._marker_event_key = t._term_key
and h._history_key = mhist._marker_key
--and h.event_date >= '03-28-22'
--and h.event_date <= now()
and h.event_date between (now() + interval '-31 day') and now()
and m1._marker_key = a1._object_key
and a1._mgitype_key = 2
and a1._logicaldb_key = 1
and a1.preferred = 1
;
create index idx1 on changed(_history_key)
;
select distinct c.event, c.oldSymbol, a.accid as oldID, c.currentSymbol, c.currentID, c.eventDate
from changed c
left outer join acc_accession a on(c._history_key = a._object_key
and a._mgitype_key = 2
and a._logicaldb_key = 1)
union
select h.event, h.history as oldSymbol, a.accid as oldID, null as currentSymbol,  null as currentID, CAST(h.event_date AS DATE) as eventDate 
from mrk_history_view h, acc_accession a
where h._marker_event_key in (106563609) -- deleted
--and h.event_date >= '03-28-22'
--and h.event_date <= now()
and h.event_date between (now() + interval '-31 day') and now()
and a._object_key = h._history_key
and a._mgitype_key = 2
and a._logicaldb_key = 1
and a.preferred = 1
order by eventDate, oldSymbol
;
