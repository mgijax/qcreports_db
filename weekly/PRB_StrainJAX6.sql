
set nocount on
go

declare @printDate varchar(255)
select @printDate = "Public JAX strains with nomen alleles but no genotype record"

print ""
print @printDate
print ""

set nocount off
go
select a.accID, s.strain
from ACC_Accession a, PRB_Strain s
where a._MGIType_key = 10
      and a._LogicalDB_key = 22
      and a._Object_key = s._Strain_key
      and s.private = 0
      and exists (select 1
                  from PRB_Strain_Marker sm
                  where sm._Strain_key = s._Strain_key
                        and sm._Qualifier_key = 615427)
      and not exists (select 1
                      from PRB_Strain_Genotype sg
                      where sg._Strain_key = s._Strain_key)
order by a.accID
go

quit

END

