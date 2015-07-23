
\echo ''
\echo 'MMRRC JRs with alleles added in past week'
\echo ''

select a.accID
from ACC_Accession a, PRB_Strain s
where a._MGIType_key = 10 and
      a._LogicalDB_key = 38 and
      a._Object_key = s._Strain_key and
      s.private = 0 and
      exists (select 1 from PRB_Strain_Marker sm
              where sm._Strain_key = s._Strain_key and
                    sm._Qualifier_key = 615427 and
                    ((sm.creation_date between (now() + interval '-7 day') and now())
                        or
                    (sm.modification_date between (now() + interval '-7 day') and now())))
order by a.accID
;

