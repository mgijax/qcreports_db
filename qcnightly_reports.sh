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

cd $QCMGD
foreach i (`ls *.sql`)
sql.sh $MGD $i
end
foreach i (`ls *.py`)
$i
end

cd $QCNOMEN
foreach i (`ls *.sql`)
sql.sh $NOMEN $i
end

