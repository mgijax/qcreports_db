#!/bin/csh -f

#
# Wrapper for calling psql with public user/password for report format
#
# Usage:
#
#	reports.sh inputfile outputfile DBSERVER DBNAME
#
# if no outputfile is specified, then will use the inputfile + ".rpt" extension
#
# HISTORY
#
# 07/23/2015
#	- TR11750/Postgres only
#
# 05/03/2011-05/09/2012	lec
#	- TR11035/add DB_TYPE/postgres option
#
# 10/06/2006	lec
#	- TR 7943; added HEADERTYPE; removed trailer
#

source `dirname $0`/Configuration

if ( ${#argv} < 4 ) then
    echo "Usage: $0 inputfile outputfile DBSERVER DBNAME [HEADERTYPE]"
    exit 0
endif

setenv INPUTFILE $1
setenv OUTPUTFILE $2
setenv DBSERVER $3
setenv DBNAME $4

echo "#" > ${OUTPUTFILE}
echo "# Date Generated:  `date`" >> ${OUTPUTFILE}
echo "# (server = ${DBSERVER}, database = ${DBNAME})" >> ${OUTPUTFILE}
echo "#" >> ${OUTPUTFILE}

psql -h ${PG_DBSERVER} -U ${PG_DBUSER} -d ${PG_DBNAME} ${PSQL_ECHO} -f${INPUTFILE} >> ${OUTPUTFILE}
