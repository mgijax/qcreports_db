set nocount on
go

select n.symbol, n.chromosome, u.login, r._Refs_key
into #temp1
from NOM_Marker n, VOC_Term t, MGI_User u, MGI_Reference_Assoc r, MGI_RefAssocType rt
where n._NomenStatus_key = t._Term_key
and t.term = 'In Progress'
and n._CreatedBy_key = u._User_key
and n._Nomen_key = r._Object_key
and r._MGIType_key = 21
and r._RefAssocType_key = rt._RefAssocType_key
and rt.assocType = 'Primary'
go

create index idx1 on #temp1(_Refs_key)
go

set nocount off
go

print ''
print 'Nomenclature In Progress Symbols'
print ''

select t.symbol, t.chromosome, t.login, jnumID = a.accID
from #temp1 t, ACC_Accession a
where t._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_Key = 1
and a.prefixPart = 'J:'
and a.preferred = 1
order by t.login, t.symbol
go
