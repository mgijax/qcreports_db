#!/usr/local/bin/python

'''
#
# Bibliographic.py 11/16/98
#
# Report:
#	List of References in Bibliographic format
#
# Usage:
#	Bibliographic.py format command
#
# where format =:
#           1  => prints author, citation, title, jnum, UI, datasets
#           2  => prints author, title, citation, jnum, datasets
#           3  => prints author, title, citation, jnum, datasets plus abstract
#
#       command = SQL select statement which returns the 
#                 desired BIB_Refs records from the database.
#                 The _Refs_key column must be included within
#                 the select statement.
#
# Generated from:
#	Editing Interface, References Report form
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

fp = reportlib.init(sys.argv[0], 'Bibliographic References', os.environ['QCREPORTOUTPUTDIR'])
reportlib.process_ref(fp, sys.argv[2], sys.argv[1])
reportlib.finish_nonps(fp)
