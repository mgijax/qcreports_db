#!/bin/csh
 
#
# Wrapper for generating SQL reports
#
# usage:  sql.sh <database> <file containing SQL commands>
#

cd `dirname $0` && source Configuration

setenv DATABASE	$1
setenv SQL	$2
setenv OUTPUT	$QCREPORTOUTPUTDIR/`basename $SQL`.rpt

cat > $OUTPUT <<END
The Jackson Laboratory - Mouse Genome Informatics - Mouse Genome Database (MGD)
Copyright 1996, 1999, 2000 The Jackson Laboratory
All Rights Reserved
Date Generated:  `date`
(SERVER=$DSQUERY;DATABASE=$MGD)

END

isql -S$DSQUERY -D$DATABASE -U$USER -P$PASSWORD -w500 -i $SQL >> $OUTPUT

cat >> $OUTPUT <<END

WARRANTY DISCLAIMER AND COPYRIGHT NOTICE
THE JACKSON LABORATORY MAKES NO REPRESENTATION ABOUT THE SUITABILITY OR 
ACCURACY OF THIS SOFTWARE OR DATA FOR ANY PURPOSE, AND MAKES NO WARRANTIES, 
EITHER EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY AND FITNESS FOR A 
PARTICULAR PURPOSE OR THAT THE USE OF THIS SOFTWARE OR DATA WILL NOT 
INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS, OR OTHER RIGHTS.  
THE SOFTWARE AND DATA ARE PROVIDED "AS IS".

This software and data are provided to enhance knowledge and encourage 
progress in the scientific community and are to be used only for research 
and educational purposes.  Any reproduction or use for commercial purpose 
is prohibited without the prior express written permission of the Jackson 
Laboratory.

Copyright © 1996, 1999, 2000 by The Jackson Laboratory
END
