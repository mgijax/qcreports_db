#!/bin/csh -f

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
    ${QCRPTS}/reports.csh $i $QCOUTPUTDIR/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
end

foreach i (*.py)
    echo `date`: $i | tee -a ${LOG}
    ${PYTHON} $i >>& ${LOG}
end

echo `date`: End monthly QC reports | tee -a ${LOG}
