#!/bin/csh

#
# qcweekly_reports.sh
#
# Script to generate weekly qc reports.
#
# Usage: qcweekly_reports.sh
#

cd `dirname $0` && source ./Configuration

#foreach i ($QCWEEKLY/*.sql)
#if ( $i == "$QCWEEKLY/ALL_ImmuneAnnot.sql" ) then
#	mv -f $QCREPORTOUTPUTDIR/`basename $i`.[0-9]*.rpt $QCALLELEARCHIVE
#	rm -rf $QCREPORTOUTPUTDIR/`basename $i`.current.rpt
#	reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.${DATE}.rpt $DSQUERY $MGD
#	ln -s $QCREPORTOUTPUTDIR/`basename $i`.${DATE}.rpt $QCREPORTOUTPUTDIR/`basename $i`.current.rpt
#else
#	reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
#endif
#end

cd weekly
foreach i (*.py)
if ( $i == "ALL_ImmuneAnnot.py" ) then
        echo "$QCREPORTOUTPUTDIR/`basename $i py`[0-9]*.html"
	mv -f $QCREPORTOUTPUTDIR/`basename $i py`[0-9]*.html $QCALLELEARCHIVE
	rm -rf $QCREPORTOUTPUTDIR/`basename $i py`current.html
	$i
	ln -s $QCREPORTOUTPUTDIR/`basename $i py`${DATE}.html $QCREPORTOUTPUTDIR/`basename $i py`current.html
else
	$i
endif
end

cd $QCREPORTOUTPUTDIR
foreach i (NOM_BroadcastReserved.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

