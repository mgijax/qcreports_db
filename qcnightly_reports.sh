#!/bin/csh

#
# qcnightly_reports.sh
#
# Script to generate nightly qc reports.
#
# Usage: qcnightly_reports.sh
#

cd `dirname $0` && source Configuration

umask 002

foreach i ($QCMGD/*.sql)
reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
end

foreach i ($QCNOMEN/*.sql)
reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $NOMEN
end

cd $QCMGD
foreach i (*.py)
$i
end

cd $QCNOMEN
foreach i (*.py)
$i
end

#
# Copy Nomen Reserved Report to private HUGO directory
#

rcp $QCREPORTOUTPUTDIR/NOMEN_Reserved.rpt $HUGODIR
rcp $QCREPORTOUTPUTDIR/NOMEN_Pending.rpt $HUGODIR

