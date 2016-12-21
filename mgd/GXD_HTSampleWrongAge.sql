\echo ''
\echo 'Samples where relevance = Yes and Age either ''postnatal'', ''postnatal adult'', ''postnatal newborn'' but age range entered'
\echo ''

select a.accID as exptId, s.name, s.age
from GXD_HTSample s, ACC_Accession a
    where s._Relevance_key = 20475450
    and (
          s.age ~ 'postnatal [0-9]'
          or
          s.age ~ 'postnatal adult [0-9]'
          or
          s.age ~ 'postnatal newborn [0-9]'
    )
    and s._Experiment_key = a._Object_key
    and a._MGIType_key = 42
    and a._LogicalDB_key = 189
    and a.preferred = 1
;

\echo ''
\echo 'Samples where relevance = Yes and postnatal age in (''day 0'', ''day 0.5'', ''day 1'', ''day 1.5'', ''day 2'', ''day 2.5'', ''day 3'', ''day 3.5'', ''newborn''), but not TS27'
\echo ''
select _Experiment_key
into temporary table temp1
from GXD_HTSample 
where _Stage_key = 27
;

create index idx1 on temp1(_Experiment_key)
;

select a.accid as exptId, s.name, s.age, s._Stage_key
from GXD_HTSample s, ACC_Accession a
where s._Relevance_key = 20475450
and s._Experiment_key = a._Object_key
and a._MGIType_key = 42
and a._LogicalDB_key = 189
and a.preferred = 1
and 
(
s.age = 'postnatal day 0' or
s.age = 'postnatal day 0.5' or
s.age = 'postnatal day 1' or
s.age = 'postnatal day 1.5' or
s.age = 'postnatal day 2' or
s.age = 'postnatal day 2.5' or
s.age = 'postnatal day 3' or
s.age = 'postnatal day 3.5' or
s.age like 'postnatal newborn%'
)
and not exists (select 1
from temp1 t
where s._Experiment_key = t._Experiment_key)
order by a.accid, s.name
;
