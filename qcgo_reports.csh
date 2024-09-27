#!/bin/csh -f

#
# qcgxd_reports.csh
#
# Script to generate nightly GO QC reports.
#
# Usage: qcgxd_reports.csh
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

echo `date`: Start nightly GO QC reports | tee -a ${LOG}

cd ${QCMGD}

foreach i (*GO*.sql)
    echo `date`: $i | tee -a ${LOG}
    ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
end

foreach i (*GO*.py VOC_InvalidInferred.py VOC_InvalidProperties.py)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GO_stats.py" ) then
        mv -f ${QCOUTPUTDIR}/`basename $i py`[0-9]*.rpt ${QCGOARCHIVE}
        rm -rf ${QCOUTPUTDIR}/`basename $i py`current.rpt
        ${PYTHON} $i >>& ${LOG}
        ln -s ${QCOUTPUTDIR}/`basename $i py`${DATE}.rpt ${QCOUTPUTDIR}/`basename $i py`current.rpt
    else
         ${PYTHON} $i >>& ${LOG}
    endif
end

cd ${QCMONTHLY}

foreach i (*GO*.sql)
    echo `date`: $i | tee -a ${LOG}
    ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
end

foreach i (*GO*.py)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GO_stats.py" ) then
        mv -f ${QCOUTPUTDIR}/`basename $i py`[0-9]*.rpt ${QCGOARCHIVE}
        rm -rf ${QCOUTPUTDIR}/`basename $i py`current.rpt
        ${PYTHON} $i >>& ${LOG}
        ln -s ${QCOUTPUTDIR}/`basename $i py`${DATE}.rpt ${QCOUTPUTDIR}/`basename $i py`current.rpt
    else
         ${PYTHON} $i >>& ${LOG}
    endif
end

echo `date`: End nightly GO QC reports | tee -a ${LOG}
