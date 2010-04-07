#!/bin/csh

#
# qcweekly_reports.sh
#
# Script to generate weekly qc reports.
#
# Usage: qcweekly_reports.sh
#
# convert to bourne shell
#

cd `dirname $0` && source ./Configuration

setenv LOG      ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

date >> ${LOG}

foreach i (${QCWEEKLY}/*.sql)
echo $i, `date` | tee -a ${LOG}
if ( $i == "${QCWEEKLY}/GXD_Triage.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCGXDARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else if ( $i == "${QCWEEKLY}/NOM_Triage.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCNOMENARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else if ( $i == "${QCWEEKLY}/MLD_Triage.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCMLDARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else if ( $i == "${QCWEEKLY}/PRB_StrainJAX4.sql" || $i == "${QCWEEKLY}/PRB_StrainJAX5.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCSTRAINARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else if ( $i == "${QCWEEKLY}/PRB_StrainJAX7.sql" || $i == "${QCWEEKLY}/PRB_StrainJAX8.sql" ) then
	mv -f ${QCOUTPUTDIR}/`basename $i`.[0-9]*.rpt ${QCSTRAINARCHIVE}
	rm -rf ${QCOUTPUTDIR}/`basename $i`.current.rpt
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
	ln -s ${QCOUTPUTDIR}/`basename $i`.${DATE}.rpt ${QCOUTPUTDIR}/`basename $i`.current.rpt
else
	reportisql.csh $i ${QCOUTPUTDIR}/`basename $i`.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
endif
echo $i, `date` | tee -a ${LOG}
end

cd weekly
foreach i (*.py)
if ( $i == "ALL_ImmuneAnnot.py" || $i == "ALL_Progress.py" ) then
        echo "$QCOUTPUTDIR/`basename $i py`[0-9]*.rpt" | tee -a ${LOG}
	mv -f $QCOUTPUTDIR/`basename $i py`[0-9]*.rpt $QCALLELEARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i py`current.rpt
	$i >>& ${LOG}
	ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.rpt $QCOUTPUTDIR/`basename $i py`current.rpt
else if ( $i == "PRB_StrainJAX2.py" ) then
        echo "$QCOUTPUTDIR/`basename $i py`jrs.[0-9]*.rpt" | tee -a ${LOG}
        echo "$QCOUTPUTDIR/`basename $i py`mmnc.[0-9]*.rpt" | tee -a ${LOG}
	mv -f $QCOUTPUTDIR/`basename $i py`jrs.[0-9]*.rpt $QCSTRAINARCHIVE
	mv -f $QCOUTPUTDIR/`basename $i py`mmnc.[0-9]*.rpt $QCSTRAINARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i py`jrs.current.rpt
	rm -rf $QCOUTPUTDIR/`basename $i py`mmnc.current.rpt
	$i >>& ${LOG}
	ln -s $QCOUTPUTDIR/`basename $i py`jrs.${DATE}.rpt $QCOUTPUTDIR/`basename $i py`jrs.current.rpt
	ln -s $QCOUTPUTDIR/`basename $i py`mmnc.${DATE}.rpt $QCOUTPUTDIR/`basename $i py`mmnc.current.rpt
else if ( $i == "MTB_Triage.py" ) then
        echo "$QCOUTPUTDIR/`basename $i py`[0-9]*.txt" | tee -a ${LOG}
	mv -f $QCOUTPUTDIR/`basename $i py`[0-9]*.txt $QCMTBARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i py`current.txt
	$i >>& ${LOG}
	ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.txt $QCOUTPUTDIR/`basename $i py`current.txt
else
	$i >>& ${LOG}
endif
end

date >> ${LOG}

