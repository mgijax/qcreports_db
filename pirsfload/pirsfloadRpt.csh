#!/bin/csh -f
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
#  Handle DB Flipping
#
if ( ${DB_TYPE} == "postgres" ) then
	setenv MGD_DBSERVER ${PG_DBSERVER}
	setenv MGD_DBNAME ${PG_DBNAME}
endif


#
# DB-Specific files - remove sybase logic/file when removing flipibility
#
if ( ${DB_TYPE} == "postgres" ) then
  DuplicateTermNames.py ${OUTPUTDIR} ${JOBKEY}
else
  DuplicateTermNamesSybase.py ${OUTPUTDIR} ${JOBKEY}
endif

OtherMarkerTypes.py ${OUTPUTDIR} ${JOBKEY}




foreach RPT (*.sql)
   ${MGI_DBUTILS}/bin/reportisql.csh $RPT ${OUTPUTDIR}/`basename $RPT`.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
end

# this is klunky...we just want to sort this report
cd ${OUTPUTDIR}
rm -rf oneToMany.rpt
sort -k1 oneToMany.txt > oneToMany.rpt

exit 0

