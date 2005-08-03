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

./strainAllele.sh >>& ${LOG}
./strainChanges.sh >>& ${LOG}
./goStats.sh >>& ${LOG}

foreach i (${QCMGD}/*.sql)
echo $i, `date`
if ( $i == "${QCMGD}/MRK_MarkerClip.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCALLELEARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${DSQUERY} ${MGD}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.rpt ${DSQUERY} ${MGD}
endif
echo $i, `date`
end

cd ${QCMGD}
foreach i (*.py)
echo $i, `date`
$i >>& ${LOG}
echo $i, `date`
end

cd ${QCOUTPUTDIR}
foreach i (NOMEN_Reserved.rpt NOMEN_Pending.rpt HMD_SymbolDiffs2.rpt)
rcp $i ${HUGOWEBDIR}
rcp $i ${HUGOFTPDIR}
end

rcp ${HUGOFASTANOMENFASTA} ${HUGOWEBDIR}
