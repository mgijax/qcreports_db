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
foreach i (`ls $QCMGD/*.py`)
$i
end

foreach i (`ls $QCNOMEN/*.sql`)
sql.sh $NOMEN $i
end

