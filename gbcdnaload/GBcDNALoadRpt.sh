#!/bin/csh
#
#  $Header$
#  $Name$
#
#  GBcDNALoadRpt.sh
###########################################################################
#
#  Purpose:  This script runs the GenBank EST cDNA clone load QC reports.
#
#  Usage:
#
#      GBcDNALoadRpt.sh  OutputDir  Server  RADAR  JobKey
#
#      where
#
#          OutputDir is the directory where the report files are created.
#          Server is the database server to use.
#          RADAR is the name of the RADAR database to use.
#          JobKey is the value that identifies the records in the RADAR
#                 QC report tables that are to be processed.
#
#  Env Vars:
#
#      None
#
#  Inputs:
#
#      - Shell script arguments (See Usage)
#
#  Outputs:
#
#      - An output file created by each QC report.
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  Fatal error occurred
#      2:  Non-fatal error occurred
#
#  Assumes:  Nothing
#
#  Implementation:  Each python script in the directory is executed to
#                   produce the reports.
#
#  Notes:  None
#
###########################################################################

cd `dirname $0` && source ../Configuration

#
#  Verify the argument(s) to the shell script.
#
if  ( ${#argv} != 4 ) then
    echo "Usage: $0  OutputDir  Server  RADAR  JobKey"
    exit 1
else
    setenv OUTPUTDIR $1
    setenv SERVER $2
    setenv RADAR $3
    setenv JOBKEY $4
endif

#
#  Run each Python report found in the directory.
#
cd `dirname $0`

foreach RPT (*.py)
    ${RPT} ${OUTPUTDIR} ${SERVER} ${RADAR} ${JOBKEY}
end

exit 0


#  $Log$
#
###########################################################################
#
# Warranty Disclaimer and Copyright Notice
#
#  THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR
#  ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES,
#  EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A
#  PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT
#  INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.
#  THE SOFTWARE AND DATA ARE PROVIDED "AS IS".
#
#  This software and data are provided to enhance knowledge and encourage
#  progress in the scientific community and are to be used only for research
#  and educational purposes.  Any reproduction or use for commercial purpose
#  is prohibited without the prior express written permission of The Jackson
#  Laboratory.
#
# Copyright \251 1996, 1999, 2002, 2004 by The Jackson Laboratory
#
# All Rights Reserved
#
##########################################################################
