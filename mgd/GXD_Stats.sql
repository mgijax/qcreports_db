set nocount on
go

/* cDNAs */

print ""
print "IMAGE cDNAs and ESTs:"

declare @washUdb int, @ref int
select @washUdb = _LogicalDB_key
from ACC_LogicalDB
where name like "WashU%"

select @ref = _Object_key
from ACC_Accession a
where accID = "J:57656"			/* WashU/dbEST load reference */

select "IMAGE cDNAs", count(p._Probe_key) 
from PRB_Probe p, VOC_Term v
where p.name like "IMAGE clone%" 
and p._SegmentType_key = v._Term_key
and v.term = "cDNA"

union all
/* Count EST accession IDs associated with these clones */
select "ESTs", count(distinct a.accID)
from ACC_Accession a, PRB_Probe p, VOC_Term t
where a._LogicalDB_key = @washUdb
and a._MGIType_key = 3 
and a._Object_key = p._Probe_key
and p.name like "IMAGE clone%" 
and p._SegmentType_key = t._Term_key
and t.term = "cDNA"

union all
select "Putative Genes", count(distinct _Marker_key)
from PRB_Marker
where relationship = 'P'

/* distinct cDNAs w/ relationships to Genes */
union all
select "cDNAs with Putative Relationships",
count (distinct pm._Probe_key)
from PRB_Marker pm, PRB_Probe p, VOC_Term t
where relationship = "P"
and p._Probe_key = pm._Probe_key
and p._SegmentType_key = t._Term_key
and t.term = "cDNA"
go


/* GXD Index Stats */
print ""
print ""
print "GXD Index Stats:"

/* Genes indexed in GXD_Index */

select "Genes Indexed", "count" = count(distinct i._Marker_key)
from GXD_Index i  

union all

/* References indexed in GXD_Index */
select "References Indexed", count(distinct _Refs_key)
from GXD_Index i

union all

/* # Gene-Reference associations */
select "Index entries", count(*)
from GXD_Index
go

print ""
print "Genes in GXD-Index by their assay type:"
select "Assay Type" = substring(v.term, 1, 35), "Genes" = count(distinct _Marker_key)
from GXD_Index i, GXD_Index_Stages s, VOC_Term_GXDIndexAssay_View v
where i._Index_key = s._Index_key
and s._IndexAssay_key = v._Term_key
group by v.term
order by v.term
go	   

/* GXD Assay counts: */
print ""
print ""
print "GXD Assay and Results:"
print ""

/* number of references in GXD assays */
select "Assay References" = count(distinct _Refs_key) 
from GXD_Assay
go

/* summarize into a temptable by input source */
declare @freemanRef int
select @freemanRef = (select _Object_key from ACC_Accession
	   where accID = 'J:46439')

select 
	/* if _Refs_key == freemanRef then 1 else 0 */
	eds = (1 - abs(sign(_Refs_key-@freemanRef))),
	cnt = count ( distinct _Marker_key  )
into #assayGenes
from GXD_Assay
group by (1 - abs(sign(_Refs_key-@freemanRef)))
go

declare @freemanRef int
select @freemanRef = (select _Object_key from ACC_Accession
	   where accID = 'J:46439')

/* Assay & results by source */
print ""
print "Assays, Assay results and genes by source:"
print ""

/* Assays by Source */
declare @distinctGenes int
select @distinctGenes = count (distinct _Marker_key) from GXD_Assay

select "Assays",
	/* sum ( if eds 1 else 0 ) */
	"Electronic Submission" = SUM (1 - abs(sign(_Refs_key-@freemanRef))),
	/* sum ( if not eds 1 else 0 )*/
	"Literature Curated" = SUM (abs(sign(_Refs_key-@freemanRef))),
	"Total" = count(*)
from GXD_Assay

union all

/* Assay results by Source */
select "Assay Results",
	/* sum ( if eds 1 else 0 ) */
	"Electronic Submission" = SUM (1 - abs(sign(_Refs_key-@freemanRef))),
	/* sum ( if not eds 1 else 0 ) */
	"Literature Curated" = SUM (abs(sign(_Refs_key-@freemanRef))),
	"Total" = count(*)
from GXD_Expression e

union all

/* Genes associated with Assays by source */
select  "Genes",
	/* sum ( if eds then 1 else 0 ) */
	"Electronic Submission" = sum(cnt * eds), 
	/* sum ( if not eds then 1 else 0 ) */
	"Literature Curated" = sum(cnt * abs (sign(eds - 1) ) ),
	"Total" = @distinctGenes
from #assayGenes

drop table #assayGenes 
go

/* Gene acquisition stats by month-year */
select     Year  = convert(numeric(4), datepart(year, a.creation_date)), 
	   Month = convert(numeric(2), datepart(month, a.creation_date)), 
	   Genes = count ( distinct _Marker_key ),
	   Refs  = count ( distinct _Refs_key )
into #assayGenes
from GXD_Assay a
group by datepart(year, a.creation_date), 
	 datepart(month, a.creation_date)
go


select distinct 
	   Year    = convert(numeric(4), datepart(year, creation_date)),
	   Month   = convert(numeric(2), datepart(month, creation_date))
into #periods
from GXD_Assay

/* Result acquisition stats by month/year periods & AssayTypes */
/* table with all rows & columns needed to accummulate these counts*/
select Year,
	   Month,
	   t._AssayType_key,
	   assayType = convert (varchar(25), t.assayType),
	   Assays=0,
	   Results=0
into #periodCounts
from #periods p, GXD_AssayType t
where t._AssayType_key > 0
go

drop table #periods
go

/* Count the Assays by period and assay type */
select Year    = convert(numeric(4), datepart(year, a.creation_date)), 
	   Month   = convert(numeric(2), datepart(month, a.creation_date)),
	   _AssayType_key,
	   Assays = count(*) 
into #assays
from GXD_Assay a
group by datepart(year, a.creation_date),
		 datepart(month, a.creation_date),
		 _AssayType_key

update #periodCounts
set Assays = a.Assays
from #periodCounts p, #assays a
where a.Year = p.Year
and a.Month = p.Month
and a._AssayType_key = p._AssayType_key
go

drop table #assays
go

/* get detailed counts for period and period-AssayType counts */
/* ... for Gel Results */
select Year    = convert(numeric(4), datepart(year, a.creation_date)), 
	   Month   = convert(numeric(2), datepart(month, a.creation_date)),
	   _AssayType_key,
	   Results = count (*)
into #gelresults
from GXD_Assay a, GXD_GelLane l, GXD_GelLaneStructure gls
where a._Assay_key = l._Assay_key
and l._GelControl_key = 1
and l._GelLane_key = gls._GelLane_key
group by datepart(year, a.creation_date), 
		 datepart(month, a.creation_date),
		 _AssayType_key


update #periodCounts
set Results = p.Results + r.Results
from #periodCounts p, #gelresults r
where r.Year = p.Year
and r.Month = p.Month
and r._AssayType_key = p._AssayType_key

go

/* ... for InSitu Results */
select Year    = convert(numeric(4), datepart(year, a.creation_date)), 
	   Month   = convert(numeric(2), datepart(month, a.creation_date)), 
	   _AssayType_key,
	   Results   = count (*)
into #insituResults
from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs
where a._Assay_key = s._Assay_key
and s._Specimen_key = r._Specimen_key
and r._Result_key = rs._Result_key
group by datepart(year, a.creation_date), 
		 datepart(month, a.creation_date),
		 _AssayType_key
go

update #periodCounts
set Results = p.Results + r.Results
from #periodCounts p, #insituresults r
where r.Year = p.Year
and r.Month = p.Month
and r._AssayType_key = p._AssayType_key
go


/* remove any assay types for which we have no results */
delete #periodCounts
from #periodCounts p
where exists ( select 1 from #periodCounts pc
where p._AssayType_key = pc._AssayType_key
group by pc._AssayType_key
having sum (pc.Assays) = 0
)

/* report the results */
print ""
print "Gene and Result counts by monthly period:"
print ""
/* 
	#assayGenes is 1-to-many with #periodCounts
	avg(Gene) & avg(References) to get single value from #assayGenes
*/
select g.Year,
	   "Mo." = g.Month,
	   Genes = avg (g.Genes),
	   Results = sum (r.Results),
	   "References" = avg (g.refs)
from #assayGenes g, #periodCounts r
where g.Year = r.Year and g.Month = r.Month
group by g.Year, g.Month
compute sum ( sum (r.Results) )
go


/* assay and result counts by Experiment-Types and month/year: */
print ""
print "Assays and results by Assay-Type and monthly period:"
print ""

select assayType, Year, "Mo"=Month, Assays, Results
from #periodCounts
order by AssayType, Year, Month
compute sum(Assays), sum(Results) by assayType
go

