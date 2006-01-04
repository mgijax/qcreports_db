#!/bin/csh -f

# $Header$
# $Name$

#
# Program: loadQC_MS_InvalidLibrary.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load the Molecular Source Processor QC_MS_InvalidLibrary table
#	with data from the specified Job Stream.
#
# Requirements Satisfied by This Program:
#
#	JSAM
#
# Usage:
#
#	loadQC_MS_InvalidLibrary.csh [RADAR DB Schema path] [MGD Database Name] [Job Stream Key] [Output Directory]
#
# Envvars:
#
# Inputs:
#
# Outputs:
#
#	QC_MS_InvalidLibrary.rpt
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

setenv RDRSCHEMADIR $1
setenv MGDDBNAME $2
setenv JOBSTREAM $3
setenv OUTPUTDIR $4

source ../Configuration
source ${RDRSCHEMADIR}/Configuration

setenv LOG ${OUTPUTDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG
 
date >> $LOG
 
cat - <<EOSQL | doisql.csh $0 >> $LOG

use $DBNAME
go

delete from QC_MS_InvalidLibrary where _JobStream_key = ${JOBSTREAM}
go

declare @startDate char(10)
select @startDate = convert(char(10), start_date, 101)
from APP_JobStream
where _JobStream_key = ${JOBSTREAM}

select s.rawLibrary
into #all
from ${MGDDBNAME}..SEQ_Sequence_Raw s, ${MGDDBNAME}..SEQ_Source_Assoc sa, ${MGDDBNAME}..PRB_Source ps
where convert(char(10), s.modification_date, 101) >= @startDate
and s.rawLibrary is not null
and s.rawLibrary != "Not Loaded"
and s._Sequence_key = sa._Sequence_key
and sa._Source_key = ps._Source_key
and ps.name is null
go

create index idx1 on #all(rawLibrary)
go

select rawLibrary, occurrences = count(rawLibrary), seq = identity(10)
into #allwithcounts
from #all
group by rawLibrary
go

declare @maxKey integer
select @maxKey = max(_QCRecord_key) + 1 from QC_MS_InvalidLibrary
if @maxKey is null
    select @maxKey = 1

insert into QC_MS_InvalidLibrary
select @maxKey + seq, ${JOBSTREAM}, rawLibrary, occurrences, getdate()
from #allwithcounts
go

checkpoint
go

quit

EOSQL

date >> $LOG

