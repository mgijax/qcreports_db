
'''
#
# WTS2-1794/SPRT-209
#
# Report:
#
# select GXD images that do not contain any Copyright
# but Reference/PDF does contain 'Creative Commons' or 'creativecommons'
# year >= 2021
# 
# Usage:
#       GXD_ImageNeedCreativeCommons.py
#
# History:
#
# lec   02/02/2026
#   wts2-1794/sprt-209/Custom report for creative commons use
#
'''

import sys
import os
import mgi_utils
import reportlib
import db

#db.setTrace(True)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

def go(form):

    sys.stdout.write('MGI ID of image stub' + TAB)
    sys.stdout.write('J#' + TAB)
    sys.stdout.write('Figure label' + CRT)

    results = db.sql('''
            select a.accID, c.jnumID, i.figureLabel
            from IMG_Image i, ACC_Accession a, BIB_Citation_Cache c, BIB_Refs r
            where i._imageclass_key = 6481781
            and not exists (select 1 from MGI_Note n
                where i._Image_key = n._Object_key
                and n._MGIType_key = 9
                and n._NoteType_key = 1023
                )
            and i._Refs_key = r._Refs_key
            and r.year >= 2021
            and i._Image_key = a._Object_key
            and a._Logicaldb_key = 1
            and a._MGIType_key = 9
            and i._Refs_key = c._Refs_key
            and exists (select 1 from BIB_Workflow_Data t
                where i._Refs_key = t._Refs_key
                and (
                    t.extractedtext like '%Creative Commons%'
                    or
                    t.extractedtext like '%creativecommons%'
                )
            )
            order by c.jnumID
            ''', 'auto')

    for r in results:

        sys.stdout.write(r['accID'] + TAB)
        sys.stdout.write(r['jnumID'] + TAB)
        sys.stdout.write(r['figureLabel'] + CRT)
            
    sys.stdout.flush()

