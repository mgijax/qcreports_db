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
echo $i, `date`
if ( $i == "$QCMGD/MRK_MarkerClip.sql" ) then
	mv -f $QCOUTPUTDIR/`basename $i`.[0-9]*.rpt $QCALLELEARCHIVE
	rm -rf $QCOUTPUTDIR/`basename $i`.current.rpt
	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.${DATE}.rpt $DSQUERY $MGD
	ln -s $QCOUTPUTDIR/`basename $i`.${DATE}.rpt $QCOUTPUTDIR/`basename $i`.current.rpt
else
	reportisql.csh $i $QCOUTPUTDIR/`basename $i`.rpt $DSQUERY $MGD
endif
echo $i, `date`
end

cd $QCMGD
foreach i (*.py)
echo $i, `date`
$i
echo $i, `date`
end

cd $QCOUTPUTDIR
foreach i (NOMEN_Reserved.rpt NOMEN_Pending.rpt HMD_SymbolDiffs2.sql.rpt)
rcp $i $HUGOWEBDIR
rcp $i $HUGOFTPDIR
end

