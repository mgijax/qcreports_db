
set nocount on
go

/* mouse markers with representative transcript sequence */
/* and no representative polypeptide sequence */

select m._Marker_key
into #markers
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Type_key = 1
and m._Marker_Status_key  in (1,3)
and exists (select 1 from SEQ_Marker_Cache sc
	where m._Marker_key = sc._Marker_key
	and sc._Qualifier_key = 615420
	and sc._Organism_key = 1)
and not exists (select 1 from SEQ_Marker_Cache sc
	where m._Marker_key = sc._Marker_key
	and sc._Qualifier_key = 615421
	and sc._Organism_key = 1)
go

create index idx1 on #markers(_Marker_key)
go

/* number of RNAs annotated to each marker */

select m._Marker_key, rnas = count(sc._Sequence_key)
into #rnacount
from #markers m, SEQ_Marker_Cache sc
where m._Marker_key = sc._Marker_key
and sc._SequenceType_key = 316346
group by m._Marker_key
go

create index idx1 on #rnacount(_Marker_key)
go

/* longest RNA sequences annotated to each Marker */

select m._Marker_key, s.length, s._Sequence_key
into #rnalength0
from #markers m, SEQ_Marker_Cache sc, SEQ_Sequence s
where m._Marker_key = sc._Marker_key
and sc._SequenceType_key = 316346
and sc._Sequence_key = s._Sequence_key
go

create index idx1 on #rnalength0(_Marker_key)
go

select _Marker_key, maxLength = max(length)
into #rnalength1
from #rnalength0
group by _Marker_key
go

create index idx1 on #rnalength1(_Marker_key)
create index idx2 on #rnalength1(maxLength)
go

/* resolve the sequence key of the longest RNA sequence */

select r1.*, r0._Sequence_key
into #rnalength2
from #rnalength0 r0, #rnalength1 r1
where r0._Marker_key = r1._Marker_key
and r0.length = r1.maxLength
order by r1._Marker_key
go

create index idx1 on #rnalength2(_Marker_key)
create index idx2 on #rnalength2(_Sequence_key)
go

/* resolve the accession id of the longest RNA sequence */

select r._Marker_key, rnalongest = a.accID
into #rnalongest
from #rnalength2 r, ACC_Accession a
where r._Sequence_key = a._Object_key
and a._MGIType_key = 19
and a._LogicalDB_key in (9, 27)
and a.preferred = 1
go

create index idx1 on #rnalongest(_Marker_key)
go

/* NM annotated to each Marker */

select m._Marker_key, rnaseq = a.accID
into #nms
from #markers m, SEQ_Marker_Cache sc, ACC_Accession a
where m._Marker_key = sc._Marker_key
and sc._SequenceType_key = 316346
and sc._Sequence_key = a._Object_key
and a._MGIType_key = 19
and a.prefixPart = "NM_"
and a.preferred = 1
go

create index idx1 on #nms(_Marker_key)
go

select a.accID, mk._Marker_key, symbol = substring(mk.symbol,1,30), mk.name, mk.chromosome, r.rnas, c.sequenceNum
into #final1
from #markers m, #rnacount r, ACC_Accession a, MRK_Marker mk, MRK_Chromosome c
where m._Marker_key = r._Marker_key
and m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 1
and a.prefixPart = "MGI:"
and a.preferred = 1
and m._Marker_key = mk._Marker_key
and mk._Organism_key = c._Organism_key
and mk.chromosome = c.chromosome
go

create index idx1 on #final1(_Marker_key)
go

select f.accID, f.symbol, f.name, f.chromosome, f.rnas, n.rnaseq, f.sequenceNum
into #final2
from #final1 f, #nms n
where f._Marker_key = n._Marker_key
union
select f.accID, f.symbol, f.name, f.chromosome, f.rnas, r.rnalongest, f.sequenceNum
from #final1 f, #rnalongest r
where f._Marker_key = r._Marker_key
and not exists (select 1 from #nms n where f._Marker_key = n._Marker_key)
go

set nocount off
go

print ""
print "MGI genes that have Transcript Sequences but no SwissProt association"
print ""

select f.accID, f.symbol, f.chromosome, convert(char(5), f.rnas) "rnas", f.rnaseq "Refseq or Longest RNA"
from #final2 f
order by f.sequenceNum
go

