#!/bin/csh

#
# qcweekly_reports.sh
#
# Script to generate weekly qc reports.
#
# Usage: qcweekly_reports.sh
#

cd `dirname $0` && source Configuration

umask 002

#foreach i (weekly/*.sql)
#reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
#end

cd weekly
foreach i (*.py)
$i
end

cd $QCREPORTOUTPUTDIR
foreach i (NOM_BroadcastReserved.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

