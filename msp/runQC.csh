#!/bin/csh -f

#
# Program: runQC.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To execute all Molecular Source Processor QC reports
#
# Requirements Satisfied by This Program:
#
#	JSAM
#
# Usage:
#
#	runQC.csh [Job Stream Key] [Output Directory]
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
# 11/09/2006	lec
#	- removed db params
#
# 03/16/2004	lec
#	- created
#

cd `dirname $0`

#
#  Verify the argument(s) to the shell script.
#

if  ( ${#argv} != 2 ) then
    echo "Usage: $0  JobKey OutputDir"
    exit 1
else
    setenv JOBSTREAM $1
    setenv OUTPUTDIR $2
endif

source ../Configuration

setenv LOG ${OUTPUTDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}
 
date | tee ${LOG}

# load QC tables which were not loaded during execution of the MSP

foreach i (loadQC_MS_Invalid*.csh)
./$i ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
end

# execute all reports

foreach i (*.py)
./$i
end

date | tee -a ${LOG}

