#!/bin/csh

#
# qcnightly_reports.sh
#
# Script to generate nightly qc reports.
#
# Usage: qcnightly_reports.sh
#

cd `dirname $0` && source Configuration

strainChanges.sh
goStats.sh

foreach i ($QCMGD/*.sql)
reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
end

foreach i ($QCNOMEN/*.sql)
reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $NOMEN
end

cd $QCMGD
foreach i (*.py)
$i
end

cd $QCNOMEN
foreach i (*.py)
$i
end

cd $QCFANTOM
foreach i (*.py)
$i
end

cd $QCREPORTOUTPUTDIR
foreach i (NOMEN_Reserved.rpt NOMEN_Pending.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

foreach i (fantom2.mgi)
rcp $i $RIKENFTPDIR
rm -rf $i
end

