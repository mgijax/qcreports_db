#!/bin/csh

#
# strainChanges.sh
#
# Script to generate report of any Strain Name changes 
# logged in the EI Logs
#
# Usage: strainChanges.sh
#

cd `dirname $0` && source ./Configuration

umask 002

setenv OUTPUTFILE	${QCREPORTOUTPUTDIR}/PRB_Strain_NameChanges.rpt

cat > $OUTPUTFILE <<END
The Jackson Laboratory - Mouse Genome Informatics - Mouse Genome Database (MGD)
Copyright 1996, 1999, 2000 The Jackson Laboratory
All Rights Reserved
Date Generated:  `date`
(EILOGS=$EILOGFILES)

Strain Names Which Have Been Changed

END

foreach i ($EILOGFILES/*/$EILOGNAME)
echo $i >> $OUTPUTFILE
egrep "STRAIN NAME MODIFIED" $i >> $OUTPUTFILE
end

