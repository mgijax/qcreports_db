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

foreach i (`ls $QCMGD/*.sql`)
sql.sh $MGD $i
end

foreach i (`ls $QCNOMEN/*.sql`)
sql.sh $NOMEN $i
end

cd $QCMGD
foreach i (`ls *.py`)
$i
end

cd $QCNOMEN
foreach i (`ls *.py`)
$i
end

#
# Copy Nomen Reserved Report to private HUGO directory
#

rcp $QCREPORTOUTPUTDIR/NOMEN_Reserved.rpt $HUGODIR

