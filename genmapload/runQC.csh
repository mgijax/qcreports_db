#!/bin/csh -f

#
# Program: runQC.csh
#
# Purpose:
#
#	To execute all Genetic Map Loader QC reports
#
# Usage:
#
#	runQC.csh
#
# History:
#
# 07/07/2010	lec
#	- TR 9316
#

cd `dirname $0`

source ../Configuration

# execute all reports

foreach i (*.py)
    ./$i
end

