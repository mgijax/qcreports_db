
\echo ''
\echo 'Germline Transmission Checks'
\echo '  only includes alleles of status ''Approved'' or ''Autoload'''
\echo ''

\echo ''
\echo 'transmission status is germline or chimeric and transmission reference does not exist'
\echo ''

select acc.accID, substring(a.symbol,1,35) as symbol, 
substring(t.term,1,25) as "trans status", 
substring(t2.term,1,25) as "allele type"
from ALL_Allele a, VOC_Term t, VOC_Term t2, ACC_Accession acc
where a._Allele_Status_key in (847114,3983021)
and a._Transmission_key = t._Term_key
and t._Term_key in (3982951,3982952)
and a._Allele_Type_key = t2._Term_key
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and not exists (select 1 from MGI_Reference_Assoc r
where a._Allele_key = r._Object_key
and r._MGIType_key = 11
and r._RefAssocType_key = 1023)
order by a.symbol
;

\echo ''
\echo 'transmission status is not germline or chimeric and transmission reference does exist'
\echo ''

select acc.accID, substring(a.symbol,1,35) as symbol, 
substring(t.term,1,25) as "trans status", 
substring(t2.term,1,25) as "allele type"
from ALL_Allele a, VOC_Term t, VOC_Term t2, ACC_Accession acc
where a._Allele_Status_key in (847114,3983021)
and a._Transmission_key = t._Term_key
and t._Term_key not in (3982951,3982952)
and a._Allele_Type_key = t2._Term_key
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and exists (select 1 from MGI_Reference_Assoc r
where a._Allele_key = r._Object_key
and r._MGIType_key = 11
and r._RefAssocType_key = 1023)
order by a.symbol
;

\echo ''
\echo 'there is no mutant cell line and the transmission status != not applicable'
\echo ''

select acc.accID, substring(a.symbol,1,35) as symbol, 
substring(t.term,1,25) as "trans status", 
substring(t2.term,1,25) as "allele type"
from ALL_Allele a, VOC_Term t, VOC_Term t2, ACC_Accession acc
where a._Allele_Status_key in (847114,3983021)
and a._Transmission_key = t._Term_key
and t._Term_key not in (3982955)
and a._Allele_Type_key = t2._Term_key
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and not exists (select 1 from ALL_Allele_CellLine c
where a._Allele_key = c._Allele_key)
order by a.symbol
;

\echo ''
\echo 'there is a mutant cell line and the transmission status = not applicable'
\echo ''

select acc.accID, substring(a.symbol,1,35) as symbol, 
substring(t.term,1,25) as "trans status", 
substring(t2.term,1,25) as "allele type"
from ALL_Allele a, VOC_Term t, VOC_Term t2, ACC_Accession acc
where a._Allele_Status_key in (847114,3983021)
and a._Transmission_key = t._Term_key
and t._Term_key in (3982955)
and a._Allele_Type_key = t2._Term_key
and a._Allele_key = acc._Object_key
and acc._MGIType_key = 11
and acc._LogicalDB_key = 1
and acc.preferred = 1
and exists (select 1 from ALL_Allele_CellLine c
where a._Allele_key = c._Allele_key)
order by a.symbol
;

