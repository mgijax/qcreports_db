#!/bin/csh

#
# qcweekly_reports.sh
#
# Script to generate weekly qc reports.
#
# Usage: qcweekly_reports.sh
#

cd `dirname $0` && source Configuration

umask 002

# GDB report
GDBreport.sh -f

