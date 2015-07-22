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

#
# translate INPUTFILE sybase sql to postgres sql
# the first 'sed' needs to contain the input file name
# next: pipe to the next sed
# last:  pipe to psql
#
sed "s/convert(char(10),/to_char(/g" ${INPUTFILE} | \
sed "s/, 101)/, 'MM\/dd\/yyyy')/g" | \
sed "s/dateadd(day, -1, getdate())/(now() + interval '-1 day')/g" | \
sed "s/dateadd(day, -3, getdate())/(now() + interval '-3 day')/g" | \
sed "s/dateadd(day, -7, getdate())/(now() + interval '-7 day')/g" | \
sed "s/getdate()/now()/g" | \
sed "s/charindex('-',/position('-' in /g" | \
sed "s/charindex(' ',/position(' ' in /g" | \
sed "s/' as /'::text as /g" | \
psql -h ${PG_DBSERVER} -U ${PG_DBUSER} -d ${PG_DBNAME} ${PSQL_ECHO} >> ${OUTPUTFILE}
