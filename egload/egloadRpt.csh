#!/bin/csh -f
#
#  egloadRpt.sh
###########################################################################
#
#  Purpose:  This script runs the egload QC reports
#
#  Usage:
#
#      egloadRpt.sh  OutputDir  Server  RADAR  JobKey
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

