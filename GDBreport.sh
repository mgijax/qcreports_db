#!/bin/csh

#
# Usage:  GDBreport.sh DSQUERY MGD
#

cd `dirname $0` && source Configuration

setenv DOFTP	$1

setenv GDB_ADDR		syb.hsc.gdb.org
setenv GDB_LOGIN	mirror
setenv GDB_PASSWD	"dna maps"

cd $QCREPORTOUTPUTDIR

if "$DOFTP" == "-f" then
ftp -n -i << END_FTP
open $GDB_ADDR
user $GDB_LOGIN "$GDB_PASSWD"
cd Lori
get Gene.medlineid.tab
quit
END_FTP
endif

#
# Execute report of potentail mouse/human homologies
#

cd $QCREPORTINSTALLDIR
HMD_Potentials.py

