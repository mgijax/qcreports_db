#!/bin/csh

#
# qcmonthly_reports.sh
#
# Script to generate monthly qc reports.
#
# Usage: qcmonthly_reports.sh
#

cd `dirname $0` && source ./Configuration

foreach i ($QCMONTHLY/*.sql)

if ( $i == "$QCMONTHLY/ALL_Progress.sql" ) then
	mv -f $QCOUTPUTDIR/`basename $i`.[0-9]*.rpt $QCALLELEARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i`.current.rpt
	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.${DATE}.rpt $DSQUERY $MGD
	ln -s $QCOUTPUTDIR/`basename $i`.${DATE}.rpt $QCOUTPUTDIR/`basename $i`.current.rpt
else
	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
endif

end

