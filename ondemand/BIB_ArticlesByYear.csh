#!/bin/csh -f

#
# BIB_ArticlesByYear.csh 
#
# Script to generate BIB_ArticlesByYear.rpt
#
# This is a convenience wrapper script over BIB_ArticlesByYear.py that takes a
# year as parameter - see usage
#
# See BIB_ArticlesByYear.py for other ways to invoke that script written by Joel
#

setenv usage "usage: BIB_ArticlesByYear.csh <year> Connie typically wants 5 years back so if it is 2022 the parameter would be 2017"

cd `dirname $0` && source ../Configuration

setenv LOG ${QCLOGSDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

echo $1
if ( $1 == "" ) then
    echo $usage
    exit 
endif

echo `date`: Start BIB_ArticlesByYear.csh | tee -a ${LOG}

 ${PYTHON} ./BIB_ArticlesByYear.py -y $1 > ${QCOUTPUTDIR}/BIB_ArticlesByYear.rpt

echo `date`: End BIB_ArticlesByYear.csh | tee -a ${LOG}
