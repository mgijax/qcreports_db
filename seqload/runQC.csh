#!/bin/csh -f

#
# Program: runQC.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To execute all Sequence Loader QC reports
#
# Requirements Satisfied by This Program:
#
#	JSAM
#
# Usage:
#
#	runQC.csh [RADAR DB Schema path] [MGD Database Name] [Job Stream Key] [Output Directory]
#
# Envvars:
#
# Inputs:
#
# Outputs:
#
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
# 03/30/2004	lec
#	- created
#

cd `dirname $0`

#
#  Verify the argument(s) to the shell script.
#

if  ( ${#argv} != 2 ) then
    echo "Usage: $0 JobKey OutputDir"
    exit 1
else
    setenv JOBSTREAM $1
    setenv OUTPUTDIR $2
endif

source ../Configuration

setenv LOG ${OUTPUTDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee ${LOG}

# execute all reports

foreach i (*.py)
./$i ${OUTPUTDIR} ${JOBSTREAM} ${MGD_DBNAME}
end

date | tee -a ${LOG}

