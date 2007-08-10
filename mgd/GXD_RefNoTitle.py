#!/usr/local/bin/python

'''
#
# TR 8394
#
# Report:
#
#       Papers lacking a title.
#
# Usage:
#       GXD_RefNoTitle.py
#
# Notes:
#
# History:
#
# dbm	08/10/2007
#	- new
#
'''

import sys
import os
import string
import re
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'GXD references lacking titles', outputdir = os.environ['QCOUTPUTDIR'])

results = db.sql('select b.jnumID ' + \
                 'from BIB_View b ' + \
                 'where b.title is null and ' + \
                       'exists (select 1 from GXD_Assay a ' + \
                               'where b._Refs_key = a._Refs_key)', 'auto')

for r in results:
    fp.write(r['jnumID'] + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
