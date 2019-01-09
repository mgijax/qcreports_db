select _logicaldb_key, accid, count(_object_key) as dupCount
   into temporary table dups
   from acc_accession
   where _logicaldb_key in (29,65)
   and _mgitype_key = 1
   group by _logicaldb_key, accid
   having count(*) > 1
   order by _logicaldb_key, accid
;

create index idx1 on dups(_LogicalDB_key)
;

\echo ''
\echo 'References with Duplicate PubMed and DOI IDs'
\echo 'Col1: Source Col2: accID Col3: Dup Count'
\echo ''

select ldb.name, d.accid, d.dupCount
from ACC_LogicalDB ldb, dups d
where d._LogicalDB_key = ldb._LogicalDB_key
;
 
