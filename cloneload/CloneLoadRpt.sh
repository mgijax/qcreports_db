#!/bin/csh
#
#  $Header$
#  $Name$
#
#  CloneLoadRpt.sh
###########################################################################
#
#  Purpose:  This script runs the clone loader QC reports.
#
#  Usage:
#
#      CloneLoadRpt.sh  OutputDir  Server  RADAR  MGD  JobKey
#
#      where
#
#          OutputDir is the directory where the report files are created.
#          Server is the database server to use.
#          RADAR is the name of the RADAR database to use.
#          MGD is the name of the MGD database to use.
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
if  ( ${#argv} != 5 ) then
    echo "Usage: $0  OutputDir  Server  RADAR  MGD  JobKey"
    exit 1
else
    setenv OUTPUTDIR $1
    setenv SERVER $2
    setenv RADAR $3
    setenv MGD $4
    setenv JOBKEY $5
endif

#
#  Run each Python report found in the directory.
#
cd `dirname $0`

foreach RPT (*.py)
    ${RPT} ${OUTPUTDIR} ${SERVER} ${RADAR} ${MGD} ${JOBKEY}
end

exit 0


#  $Log$
#  Revision 1.2  2004/08/16 14:57:07  lec
#  qcreports_db-23-0-6
#
#  Revision 1.1.2.1  2004/07/09 15:14:01  dbm
#  Moved from parent directory
#
#  Revision 1.1  2004/07/09 13:46:36  dbm
#  Moved from parent directory
#
#  Revision 1.2  2003/11/21 18:24:58  dbm
#  Converted to csh
#
#  Revision 1.1  2003/11/07 19:31:16  dbm
#  Initial version
#
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
# Copyright \251 1996, 1999, 2002, 2003 by The Jackson Laboratory
#
# All Rights Reserved
#
##########################################################################
