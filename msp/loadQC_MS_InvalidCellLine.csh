#!/bin/csh -f

#
# Program: loadQC_MS_InvalidCellLine.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load the Molecular Source Processor QC_MS_InvalidCellLine table
#	with data from the specified Job Stream.
#
# Requirements Satisfied by This Program:
#
#	JSAM
#
# Usage:
#
#	loadQC_MS_InvalidCellLine.csh [RADAR DB Schema path] [MGD Database Name] [Job Stream Key] [Output Directory]
#
# Envvars:
#
# Inputs:
#
# Outputs:
#
#	QC_MS_InvalidCellLine.rpt
#	log file
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#
#    Modules:
#
# Modification History:
#
# 03/16/2004 lec
#	- created
#

setenv JOBSTREAM $1
setenv OUTPUTDIR $2

source ../Configuration

setenv LOG ${OUTPUTDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG
 
date >> $LOG
 
cat - <<EOSQL | doisql.csh ${RADAR_DBSCHEMADIR} ${RADAR_DBNAME} $0 >> $LOG

use ${RADAR_DBNAME}
go

delete from QC_MS_InvalidCellLine where _JobStream_key = ${JOBSTREAM}
go

declare @startDate char(10)
select @startDate = convert(char(10), start_date, 101)
from APP_JobStream
where _JobStream_key = ${JOBSTREAM}

select s.rawCellLine
into #all
from ${MGD_DBNAME}..SEQ_Sequence_Raw s, ${MGD_DBNAME}..SEQ_Source_Assoc sa, ${MGD_DBNAME}..PRB_Source ps
where convert(char(10), s.modification_date, 101) >= @startDate
and s.rawCellLine is not null
and s.rawCellLine != "Not Loaded"
and s._Sequence_key = sa._Sequence_key
and sa._Source_key = ps._Source_key
and ps._CellLine_key = 316337
go

create index idx1 on #all(rawCellLine)
go

select rawCellLine, occurrences = count(rawCellLine), seq = identity(10)
into #allwithcounts
from #all
group by rawCellLine
go

declare @maxKey integer
select @maxKey = max(_QCRecord_key) + 1 from QC_MS_InvalidCellLine
if @maxKey is null
    select @maxKey = 1

insert into QC_MS_InvalidCellLine
select @maxKey + seq, ${JOBSTREAM}, rawCellLine, occurrences, getdate()
from #allwithcounts
go

checkpoint
go

quit

EOSQL

date >> $LOG

