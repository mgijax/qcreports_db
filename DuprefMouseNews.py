#!/usr/local/bin/python

'''
#
# DuprefMouseNews.py 11/16/98
#
# Report:
#       List of Duplicate References in Bibliographic format
#       for 'Mouse News Letter' 
#	Excluding Guidi numbers (J:5000 - J:11810)
#
# Usage:
#       DuprefMouseNews.py
#
# Generated from:
#       Editing Interface, References Report form
#
# Notes:
#       Duplicates are determined by grouping References by
#       first author (_primary), journal, volume (vol), pages (pgs) and year
#
# History:
#
# lec	01/13/98
#	- added comments
#
'''
 
import sys
import os
import reportlib

cmd = 'select _Refs_key from BIB_View ' + \
'where (jnum < 5001 or jnum > 11810) and journal like "Mouse%News%Lett%" ' + \
'group by _primary, journal, vol, pgs, year having count(*) > 1 ' + \
'order by _primary, journal, year'
fp = reportlib.init(sys.argv[0], 'Duplicate References for Mouse News Letter', os.environ['QCREPORTOUTPUTDIR'])
reportlib.process_ref(fp, cmd)
reportlib.finish_nonps(fp)
