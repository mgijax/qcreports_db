#!/bin/csh

#
# qcweekly_reports.sh 07/21/99
#
# Script to generate weekly qc reports.
#
# Usage: qcweekly_reports.sh
#

cd `dirname $0` && source Configuration

umask 002

set RPTS="MRK_NomenUpdates.py"

foreach i ("$RPTS")
$i
end

