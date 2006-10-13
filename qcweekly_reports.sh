#!/bin/csh

#
# qcweekly_reports.sh
#
# Script to generate weekly qc reports.
#
# Usage: qcweekly_reports.sh
#

cd `dirname $0` && source ./Configuration

setenv LOG      ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

date >> ${LOG}

#foreach i (${QCWEEKLY}/*.sql)
foreach i (${QCWEEKLY}/NOM_Triage.sql)	## REMOVE BEFORE TAGGING
echo $i, `date` | tee -a ${LOG}
if ( $i == "${QCWEEKLY}/GXD_Triage.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCGXDARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else if ( $i == "${QCWEEKLY}/NOM_Triage.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCNOMENARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	setenv MGD_DBSERVER DEV_MGI
	setenv MGD_DBNAME mgd
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
endif
echo $i, `date` | tee -a ${LOG}
end
exit 0	# REMOVE BEFORE TAGGING

cd weekly
foreach i (*.py)
if ( $i == "ALL_ImmuneAnnot.py" || $i == "ALL_Progress.py" ) then
        echo "$QCOUTPUTDIR/`basename $i py`[0-9]*.rpt" | tee -a ${LOG}
	mv -f $QCOUTPUTDIR/`basename $i py`[0-9]*.rpt $QCALLELEARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i py`current.rpt
	$i >>& ${LOG}
	ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.rpt $QCOUTPUTDIR/`basename $i py`current.rpt
else if ( $i == "PRB_StrainJAX2.py" ) then
        echo "$QCOUTPUTDIR/`basename $i py`[0-9]*.rpt" | tee -a ${LOG}
	mv -f $QCOUTPUTDIR/`basename $i py`[0-9]*.rpt $QCSTRAINARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i py`current.rpt
	$i >>& ${LOG}
	ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.rpt $QCOUTPUTDIR/`basename $i py`current.rpt
else
	$i >>& ${LOG}
endif
end

cd $QCOUTPUTDIR
foreach i (NOM_BroadcastReserved.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

date >> ${LOG}

