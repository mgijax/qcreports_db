#!/bin/csh -f

# $Header$
# $Name$

#
# Program: loadQC.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
# Requirements Satisfied by This Program:
#
# Usage:
#
# Envvars:
#
# Inputs:
#
# Outputs:
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
#

setenv RDRSCHEMADIR $1
setenv MGDDBNAME $2
setenv JOBSTREAM $3
setenv OUTPUTDIR $4

source ../Configuration
source ${RDRSCHEMADIR}/Configuration

setenv LOG ${QCREPORTOUTPUTDIR}/$0.log
rm -rf $LOG
touch $LOG
 
date | tee ${LOG}

./loadQC_MS_InvalidLibrary.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidStrain.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidTissue.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidCellLine.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}
./loadQC_MS_InvalidGender.csh ${RDRSCHEMADIR} ${MGDDBNAME} ${JOBSTREAM} ${OUTPUTDIR} | tee -a ${LOG}

date | tee -a ${LOG}

