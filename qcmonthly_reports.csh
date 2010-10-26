#!/bin/csh

#
# qcmonthly_reports.csh
#
# Script to generate monthly QC reports.
#
# Usage: qcmonthly_reports.csh
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

echo `date`: Start monthly QC reports | tee -a ${LOG}

cd ${QCMONTHLY}

foreach i (*.sql)
    echo `date`: $i | tee -a ${LOG}
    reportisql.csh $i $QCOUTPUTDIR/$i.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
end

foreach i (*.py)
    echo `date`: $i | tee -a ${LOG}
    $i >>& ${LOG}
end

echo `date`: End monthly QC reports | tee -a ${LOG}