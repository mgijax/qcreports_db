#!/bin/csh -f

# $Header$
# $Name$

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

if  ( ${#argv} != 4 ) then
    echo "Usage: $0  RADARDBSchemaDir MGD  JobKey OutputDir"
    exit 1
else
    setenv RDRSCHEMADIR $1
    setenv MGDDBNAME $2
    setenv JOBSTREAM $3
    setenv OUTPUTDIR $4
endif

source ../Configuration
source ${RDRSCHEMADIR}/Configuration

setenv LOG ${OUTPUTDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee ${LOG}

# execute all reports

foreach i (*.py)
./$i ${OUTPUTDIR} ${JOBSTREAM} ${MGDDBNAME}
end

date | tee -a ${LOG}

