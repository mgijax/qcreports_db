#!/bin/csh

#
# qcnightly_reports.sh 07/21/99
#
# Script to generate nightly qc reports.
#
# Usage: qcnightly_reports.sh
#

cd `dirname $0` && source Configuration

umask 002

foreach i (`ls *.sql`)
sql.sh $MGD $i
end

foreach i (`ls *.py`)
$i
end
