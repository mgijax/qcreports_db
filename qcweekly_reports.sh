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

#foreach i ($QCWEEKLY/*.sql)
#if ( $i == "$QCWEEKLY/ALL_ImmuneAnnot.sql" ) then
#	mv -f $QCOUTPUTDIR/`basename $i`.[0-9]*.rpt $QCALLELEARCHIVE
#	rm -rf $QCOUTPUTDIR/`basename $i`.current.rpt
#	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.${DATE}.rpt $DSQUERY $MGD
#	ln -s $QCOUTPUTDIR/`basename $i`.${DATE}.rpt $QCOUTPUTDIR/`basename $i`.current.rpt
#else
#	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
#endif
#end

cd weekly
foreach i (*.py)
if ( $i == "ALL_ImmuneAnnot.py" ) then
	echo $i, `date`
        echo "$QCOUTPUTDIR/`basename $i py`[0-9]*.rpt"
	mv -f $QCOUTPUTDIR/`basename $i py`[0-9]*.rpt $QCALLELEARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i py`current.rpt
	$i >>& ${LOG}
	ln -s $QCOUTPUTDIR/`basename $i py`${DATE}.rpt $QCOUTPUTDIR/`basename $i py`current.rpt
	echo $i, `date`
else
	$i
endif
end

cd $QCOUTPUTDIR
foreach i (NOM_BroadcastReserved.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

