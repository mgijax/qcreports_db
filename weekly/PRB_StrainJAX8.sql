
print ''
print 'MMRRC JR#s with alleles added in past week'
print ''

select a.accID
from ACC_Accession a, PRB_Strain s
where a._MGIType_key = 10 and
      a._LogicalDB_key = 38 and
      a._Object_key = s._Strain_key and
      s.private = 0 and
      exists (select 1 from PRB_Strain_Marker sm
              where sm._Strain_key = s._Strain_key and
                    sm._Qualifier_key = 615427 and
                    ((sm.creation_date between
                        dateadd(day, -7, getdate()) and getdate()) or
                    (sm.modification_date between
                        dateadd(day, -7, getdate()) and getdate())))
order by a.accID
go

