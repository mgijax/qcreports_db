#!/bin/csh -f

#
# strainChanges.csh
#
# Script to generate report of any Strain Name changes 
# logged in the EI Logs
#
# Usage: strainChanges.csh
#

cd `dirname $0` && source ./Configuration

umask 002

setenv OUTPUTFILE ${QCOUTPUTDIR}/PRB_Strain_NameChanges.rpt

cat > $OUTPUTFILE <<END
The Jackson Laboratory - Mouse Genome Informatics - Mouse Genome Database (MGD)
Copyright 1996, 1999, 2002, 2005, 2008 The Jackson Laboratory
All Rights Reserved
Date Generated:  `date`
(EILOGS=$EILOGFILES)

Strain Names Which Have Been Changed

END

foreach i ($EILOGFILES/*/$EILOGNAME)
    echo $i >> $OUTPUTFILE
    egrep "STRAIN NAME MODIFIED" $i >> $OUTPUTFILE
end
