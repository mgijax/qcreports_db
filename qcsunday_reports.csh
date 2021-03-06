#!/bin/csh -f

#
# qcsunday_reports.csh
#
# Script to generate Sunday QC reports.
#
#    This is intended for reports that run daily Mon-Fri (Tue-Sat morning),
#    but also need to run Sunday to make them available on Monday morning.
#
# Usage: qcsunday_reports.csh
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

echo `date`: Start Sunday QC reports | tee -a ${LOG}

cd ${QCMGD}

foreach i (GXD_ProbeAntibody.sql)
    echo `date`: $i | tee -a ${LOG}
    ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
end

echo `date`: End Sunday QC reports | tee -a ${LOG}
