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
    if ( $i == "PRB_StrainJAX4.sql" || $i == "PRB_StrainJAX5.sql" ) then
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
        ${PYTHON} $i >>& ${LOG}
        ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.rpt $QCOUTPUTDIR/`basename $i py`current.rpt
    else if ( $i == "PRB_StrainJAX2.py" ) then
        mv -f $QCOUTPUTDIR/`basename $i py`jrs.[0-9]*.rpt $QCSTRAINARCHIVE
        rm -rf $QCOUTPUTDIR/`basename $i py`jrs.current.rpt
        ${PYTHON}  $i >>& ${LOG}
        ln -s $QCOUTPUTDIR/`basename $i py`jrs.${DATE}.rpt $QCOUTPUTDIR/`basename $i py`jrs.current.rpt
    else
        ${PYTHON} $i >>& ${LOG}
    endif
end

chmod 666 ${QCGXDARCHIVE}/*.rpt

echo `date`: End weekly QC reports | tee -a ${LOG}
