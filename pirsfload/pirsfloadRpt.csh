#!/bin/csh
#
#  pirsfload.csh
###########################################################################
#
#  Purpose:  This script runs the pirsfload QC reports
#
#  Usage:
#
#      "pirsfloadRpt.csh  OutputDir JobKey
#
#      where
#
#          OutputDir is the directory where the report files are created.
#          Server is the database server to use.
#          MGD is the MGD database to use.
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
if  ( ${#argv} != 2 ) then
    echo "Usage: $0 OutputDir Server MGD RADAR JobKey"
    exit 1
else
    setenv OUTPUTDIR $1
    setenv JOBKEY $2
endif

#
#  Run each Python report found in the directory.
#

foreach RPT (*.py)
    ${RPT} ${OUTPUTDIR} ${JOBKEY}
end

foreach RPT (*.sql)
   reportisql.csh $RPT ${OUTPUTDIR}/`basename $RPT`.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
end

exit 0

