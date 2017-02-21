
\echo ''
\echo 'Alleles with status approved or autoload that have no original reference'
\echo ''

select *
into temporary table alleles
from ALL_Allele
where _Allele_Status_key in (847114, 3983021) /* approved, autoload*/
and isWildType = 0

;

create index idx1 on alleles (_Allele_key)

;

select distinct ra._Object_key
into temporary table originalRef
from MGI_Reference_Assoc ra
where ra._MGIType_key = 11 /* allele */
and ra._RefAssocType_key = 1011 /* original */

;

create index idx2 on originalRef(_Object_key)

;

select a.symbol, aa.accid
from alleles a, ACC_Accession aa
where not exists (select 1
from originalRef o
where o._Object_key = a._Allele_key)
and a._Allele_key = aa._Object_key
and aa._MGIType_key = 11
and aa._LogicalDB_key = 1
and aa.prefixPart = 'MGI:'
and aa.preferred = 1

;
