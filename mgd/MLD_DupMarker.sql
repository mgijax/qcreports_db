set nocount on
go

select distinct _Expt_key, _Marker_key
into #expts
from MLD_Expt_Marker
group by _Expt_key, _Marker_key having count(*) >= 2
go

set nocount off
go

print ""
print "Duplicate Markers Appearing in Experiments"
print ""

select distinct v._Expt_key, exptType = substring(v.exptType, 1, 30) + '-' + convert(varchar(5), v.tag),
v.symbol, v.jnum
from #expts e, MLD_Expt_Marker_View v
where e._Expt_key = v._Expt_key
and e._Marker_key = v._Marker_key
order by v.exptType, v.tag, v.jnum, v.symbol, v.sequenceNum
go

drop table #expts
go

