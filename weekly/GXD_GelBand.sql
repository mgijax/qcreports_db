
set nocount on
go

select l._Assay_key
into #assay
from GXD_GelLane l, GXD_GelBand b
where l._GelControl_key = 1
and l._GelLane_key = b._GelLane_key
and b._Strength_key = -2
go

create index idx1 on #assay(_Assay_key)
go

set nocount off
go

print ""
print "GXD Blot w/ Control = No and Strength = Not Applicable"
print ""

select distinct a.jnumID, a.mgiID
from #assay s, GXD_Assay_View a
where s._Assay_key = a._Assay_key
order by a.jnum
go
