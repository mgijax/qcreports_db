#!/bin/csh -f

#
# qcnightly_reports.csh
#
# Script to generate nightly QC reports.
#
# Usage: qcnightly_reports.csh
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

if ( ${DB_TYPE} == "postgres" ) then
    setenv MGD_DBSERVER ${PG_DBSERVER}
    setenv MGD_DBNAME ${PG_DBNAME}
endif

echo `date`: Start nightly QC reports | tee -a ${LOG}

cd ${QCMGD}

foreach i (*.sql)
    echo `date`: $i | tee -a ${LOG}
    ${MGI_DBUTILS}/bin/reportisql.csh $i ${QCOUTPUTDIR}/$i.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
end

foreach i (*.py)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GXD_Stats.py" ) then
        mv -f ${QCOUTPUTDIR}/`basename $i py`[0-9]*.rpt ${QCGXDARCHIVE}
        rm -rf ${QCOUTPUTDIR}/`basename $i py`current.rpt
        $i >>& ${LOG}
        ln -s ${QCOUTPUTDIR}/`basename $i py`${DATE}.rpt ${QCOUTPUTDIR}/`basename $i py`current.rpt
    else if ( $i == "GO_stats.py" ) then
        $i >>& ${LOG}
        cp -p ${QCOUTPUTDIR}/GO_stats.rpt ${QCGOARCHIVE}/GO_stats.`date +%Y%m%d`
    else
        $i >>& ${LOG}
    endif
end

echo `date`: End nightly QC reports | tee -a ${LOG}
