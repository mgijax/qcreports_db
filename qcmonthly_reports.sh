#!/bin/csh

#
# qcmonthly_reports.sh
#
# Script to generate monthly qc reports.
#
# Usage: qcmonthly_reports.sh
#

cd `dirname $0` && source Configuration

setenv DATE `date '+%Y-%m-%d'`

umask 002

foreach i ($QCMONTHLY/*.sql)

mv -f $QCREPORTOUTPUTDIR/`basename $i`.[0-9]*.rpt $QCALLELEARCHIVE
rm -rf $QCREPORTOUTPUTDIR/`basename $i`.current.rpt
reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.${DATE}.rpt $DSQUERY $MGD
ln -s $QCREPORTOUTPUTDIR/`basename $i`.${DATE}.rpt $QCREPORTOUTPUTDIR/`basename $i`.current.rpt

end

