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

date >> ${LOG}

foreach i ($QCMONTHLY/*.sql)
echo $i, `date` | tee -a ${LOG}
reportisql.csh $i $QCOUTPUTDIR/`basename $i`.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
echo $i, `date` | tee -a ${LOG}
end

date >> ${LOG}

