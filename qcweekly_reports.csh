#!/bin/csh -f

#
# qcweekly_reports.csh
#
# Script to generate weekly QC reports.
#
# Usage: qcweekly_reports.csh
#

cd `dirname $0` && source ./Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

echo `date`: Start weekly QC reports | tee -a ${LOG}

cd ${QCWEEKLY}

foreach i (*.sql)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GXD_Triage.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCGXDARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${PG_DBSERVER} ${PG_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else if ( $i == "PRB_StrainJAX4.sql" || $i == "PRB_StrainJAX5.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCSTRAINARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${PG_DBSERVER} ${PG_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else if ( $i == "PRB_StrainJAX7.sql" || $i == "PRB_StrainJAX8.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCSTRAINARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${PG_DBSERVER} ${PG_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else
         ${QCRPTS}/reports.csh $i ${QCOUTPUTDIR}/$i.rpt ${PG_DBSERVER} ${PG_DBNAME}
    endif
end

foreach i (*.py)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "ALL_Progress.py" || $i == "ALL_NewAllele.py" ) then
        mv -f $QCOUTPUTDIR/`basename $i py`[0-9]*.rpt $QCALLELEARCHIVE
        rm -rf $QCOUTPUTDIR/`basename $i py`current.rpt
        $i >>& ${LOG}
        ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.rpt $QCOUTPUTDIR/`basename $i py`current.rpt
    else if ( $i == "PRB_StrainJAX2.py" ) then
        mv -f $QCOUTPUTDIR/`basename $i py`jrs.[0-9]*.rpt $QCSTRAINARCHIVE
        mv -f $QCOUTPUTDIR/`basename $i py`mmrrc.[0-9]*.rpt $QCSTRAINARCHIVE
        rm -rf $QCOUTPUTDIR/`basename $i py`jrs.current.rpt
        rm -rf $QCOUTPUTDIR/`basename $i py`mmrrc.current.rpt
        $i >>& ${LOG}
        ln -s $QCOUTPUTDIR/`basename $i py`jrs.${DATE}.rpt $QCOUTPUTDIR/`basename $i py`jrs.current.rpt
        ln -s $QCOUTPUTDIR/`basename $i py`mmrrc.${DATE}.rpt $QCOUTPUTDIR/`basename $i py`mmrrc.current.rpt
    else if ( $i == "GO_stats.py" ) then
        $i >>& ${LOG}
        cp -p ${QCOUTPUTDIR}/GO_stats.rpt ${QCGOARCHIVE}/GO_stats.`date +%Y%m%d`
    else
        $i >>& ${LOG}
    endif
end

echo `date`: End weekly QC reports | tee -a ${LOG}
