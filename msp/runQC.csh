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
#	To execute all Molecular Source Processor QC reports
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
# 03/16/2004	lec
#	- created
#

cd `dirname $0`

setenv RDRSCHEMADIR $1
setenv MGDDBNAME $2
setenv JOBSTREAM $3
setenv OUTPUTDIR $4

source ../Configuration
source ${RDRSCHEMADIR}/Configuration

setenv LOG ${OUTPUTDIR}/$0.log
rm -rf $LOG
touch $LOG
 
date | tee ${LOG}

# load QC tables which were not loaded during execution of the MSP

./loadQC_MS_InvalidLibrary.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidStrain.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidTissue.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidCellLine.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidGender.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}

# execute all reports

#foreach i (*.py)
foreach i (*Invalid*.py)
./$i ${OUTPUTDIR} ${JOBSTREAM} ${MGDDBNAME}
end

date | tee -a ${LOG}

