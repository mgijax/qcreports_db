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

echo `date`: Start nightly QC reports | tee -a ${LOG}

cd ${QCMGD}

foreach i (*.sql)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GO_NotGene.sql" ) then
	${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
	cp -p ${QCOUTPUTDIR}/GO_NotGene.sql.rpt ${QCGOARCHIVE}/GO_NotGene.sql.rpt.`date +%Y%m%d`
    else
	${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
    endif
end

foreach i (*.py)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GXD_Stats.py" ) then
        mv -f ${QCOUTPUTDIR}/`basename $i py`[0-9]*.rpt ${QCGXDARCHIVE}
        rm -rf ${QCOUTPUTDIR}/`basename $i py`current.rpt
        ${PYTHON} $i >>& ${LOG}
        ln -s ${QCOUTPUTDIR}/`basename $i py`${DATE}.rpt ${QCOUTPUTDIR}/`basename $i py`current.rpt
    else if ( $i == "GO_stats.py" ) then
        ${PYTHON} $i >>& ${LOG}
        cp -p ${QCOUTPUTDIR}/GO_stats.rpt ${QCGOARCHIVE}/GO_stats.`date +%Y%m%d`
    else
         ${PYTHON} $i >>& ${LOG}
    endif
end

chmod 666 ${QCGXDARCHIVE}/*.rpt

echo `date`: End nightly QC reports | tee -a ${LOG}
