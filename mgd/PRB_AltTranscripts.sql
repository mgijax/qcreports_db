set nocount on
go

select distinct mm.symbol, pb._Probe_key, probe_name = (convert(varchar (20), pb.name))
into #csnr
from PRB_Reference pr, PRB_Source ps, PRB_Probe pb, PRB_Notes pn, MRK_Marker mm, PRB_Marker pm
where pn.note like "%alternat%"
and ps._Organism_key = 1
and pm.relationship = "E"
and pn._Probe_key = pb._Probe_key
and pb._Probe_key = pr._Probe_key
and pb._Source_key = ps._Source_key
and mm._Marker_key = pm._Marker_key
and pm._Probe_key = pb._Probe_key
go
 
set nocount off
go

print ""
print "QC report for Alterntative Transcripts public report (PRB_AltTranscripts.rpt)."
print ""
 
select distinct      c.probe_name, c._Probe_key, count(c.symbol)
from                 #csnr c
group by             c._Probe_key
having               count(c.symbol) > 1
go 

