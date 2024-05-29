#!/bin/csh -f

#
# litrriage_reports.csh
#
# Script to generate lit triage QC reports.
#
# Usage: littriage_reports.csh
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

echo `date`: Start Lit Triage reports | tee -a ${LOG}

cd ${QCWEEKLY}

foreach i (BIB_MissingDOI.sql)
    echo `date`: $i | tee -a ${LOG}
    ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
end

#foreach i (*.py)
#    echo `date`: $i | tee -a ${LOG}
#    ${PYTHON} $i >>& ${LOG}
#end

echo `date`: End Lit Triage reports | tee -a ${LOG}
