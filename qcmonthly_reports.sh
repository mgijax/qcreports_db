#!/bin/csh

#
# qcmonthly_reports.sh
#
# Script to generate monthly qc reports.
#
# Usage: qcmonthly_reports.sh
#

cd `dirname $0` && source ./Configuration

setenv LOG	${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

foreach i ($QCMONTHLY/*.sql)
	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.rpt ${MGD_DBSERVER} ${MGD_DBNAME} ${RADAR_DBNAME}
end

