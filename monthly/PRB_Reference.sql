select p._Probe_key, p.name 
INTO TEMPORARY TABLE probes
from PRB_Probe p
where not exists (select r.* from PRB_Reference r where p._Probe_key = r._Probe_key)
;

select distinct pp._Probe_key, pr._Refs_key
INTO TEMPORARY TABLE probes2
from PRB_Probe pp, PRB_Reference pr
where pp._Probe_key = pr._Probe_key
group by pp._Probe_key, pr._Refs_key having count(*) > 1
;

create index idx1_probes on probes(_Probe_key)
;
create index idx1_probes2 on probes2(_Probe_key)

;
create index idx2_probes2 on probes2(_Refs_key)
;


\echo ''
\echo 'Probes/Primers w/out References'
\echo ''

select p.name, m.symbol, p._Probe_key 
from probes p, PRB_Marker pm, MRK_Marker m
where p._Probe_key = pm._Probe_key
and pm._Marker_key = m._Marker_key
order by p.name, m.symbol
;

\echo ''
\echo 'Probes/Primers with duplicate References'
\echo ''

select pp.name, r.jnumID
from probes2 p, PRB_Probe pp, BIB_Citation_Cache r
where p._Probe_key = pp._Probe_key
and p._Refs_key = r._Refs_key
order by pp.name
;

