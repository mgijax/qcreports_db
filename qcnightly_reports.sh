#!/bin/csh

#
# qcnightly_reports.sh
#
# Script to generate nightly qc reports.
#
# Usage: qcnightly_reports.sh
#

cd `dirname $0` && source ./Configuration

setenv LOG	${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

date >> ${LOG}

./strainAllele.sh >>& ${LOG}
./strainChanges.sh >>& ${LOG}
./goStats.sh >>& ${LOG}

foreach i (${QCMGD}/*.sql)
echo $i, `date` | tee -a ${LOG}
if ( $i == "${QCMGD}/MRK_MarkerClip.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCALLELEARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
endif
echo $i, `date` | tee -a ${LOG}
end

cd ${QCMGD}
foreach i (*.py)
echo $i, `date` | tee -a ${LOG}
$i >>& ${LOG}
echo $i, `date` | tee -a ${LOG}
end

cd ${QCOUTPUTDIR}
foreach i (NOMEN_Reserved.rpt NOMEN_Pending.rpt HMD_SymbolDiffs2.rpt)
rcp $i ${HUGOWEBDIR}
cp $i ${HUGOFTPDIR}
end

rcp ${HOBBITONNOMENFASTA} ${QCOUTPUTDIR}
rcp ${QCOUTPUTDIR}/${NOMENFASTA} ${HUGOWEBDIR}

date >> ${LOG}

