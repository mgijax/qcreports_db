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

foreach i ($QCWEEKLY/*.sql)
	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
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

