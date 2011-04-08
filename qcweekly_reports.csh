#!/bin/csh

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

foreach i (MP_Triage.sql)
    echo `date`: $i | tee -a ${LOG}
    if ( $i == "GXD_Triage.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCGXDARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        reportisql.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else if ( $i == "MLD_Triage.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCMLDARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        reportisql.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else if ( $i == "PRB_StrainJAX4.sql" || $i == "PRB_StrainJAX5.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCSTRAINARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        reportisql.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else if ( $i == "PRB_StrainJAX7.sql" || $i == "PRB_StrainJAX8.sql" ) then
        mv -f ${QCOUTPUTDIR}/$i.[0-9]*.rpt ${QCSTRAINARCHIVE}
        rm -rf ${QCOUTPUTDIR}/$i.current.rpt
        reportisql.csh $i ${QCOUTPUTDIR}/$i.${DATE}.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
        ln -s ${QCOUTPUTDIR}/$i.${DATE}.rpt ${QCOUTPUTDIR}/$i.current.rpt
    else
        reportisql.csh $i ${QCOUTPUTDIR}/$i.rpt ${MGD_DBSERVER} ${MGD_DBNAME}
    endif
end

echo `date`: End weekly QC reports | tee -a ${LOG}
