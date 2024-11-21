#!/bin/bash

#
# To Test by hand...
# . set the QUERY_STRING environment variable to the encoded argument string 
# . call pwireports.cgi.
#
# In addition to ‘arg’ there are two other parameters, ‘cmd=run’ and ‘rpt=PRB_StrainRepoCheck’.
#
# examples
#
# testManual.sh PRB_StrainNomenCheck "C57BL/6-1700009J07Rik<em1Smoc>/Smoc"
#

export RPTNAME=$1
export RPTARG=$2
export QUERY_STRING="cmd=run&rpt=$RPTNAME&arg=$RPTARG"
./pwireports.cgi 

