#!/bin/csh

#
# qcnightly_reports.sh
#
# Script to generate nightly qc reports.
#
# Usage: qcnightly_reports.sh
#

cd `dirname $0` && source ./Configuration

./strainAllele.sh
./strainChanges.sh
./goStats.sh

foreach i ($QCMGD/*.sql)
if ( $i == "$QCMGD/MRK_MarkerClip.sql" ) then
	mv -f $QCREPORTOUTPUTDIR/`basename $i`.[0-9]*.rpt $QCALLELEARCHIVE
	rm -rf $QCREPORTOUTPUTDIR/`basename $i`.current.rpt
	reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.${DATE}.rpt $DSQUERY $MGD
	ln -s $QCREPORTOUTPUTDIR/`basename $i`.${DATE}.rpt $QCREPORTOUTPUTDIR/`basename $i`.current.rpt
else
	reportisql.csh $i $QCREPORTOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
endif
end

cd $QCMGD
foreach i (*.py)
$i
end

cd $QCREPORTOUTPUTDIR
foreach i (NOMEN_Reserved.rpt NOMEN_Pending.rpt HMD_SymbolDiffs2.sql.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

