
'''
#
# GXD_FCHighlight.py
#
# Full-coded by GXD
# Year of publication in the last 2 years
# Has images attached - has PIX ID’s associated with the image records of the J#
# The lit record does not have the GXD:HighlightReference tag
#
# Report lists:
# J:
# Journal
# Number of images
# Number of image panes
# Title
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

results = db.sql('''
WITH refs_fchigh AS (
select r._refs_key, r.year, c.jnumid, r.journal, r.title
from BIB_Refs r, BIB_Citation_Cache c
where r.year between date_part('year', CURRENT_DATE) - 2 and date_part('year', CURRENT_DATE)
and r._refs_key = c._refs_key
and exists (select 1 from BIB_Workflow_Status ws
        where r._refs_key = ws._refs_key
        and ws.iscurrent = 1
        and ws._group_key = 31576665
        and ws._status_key = 31576674
        )
and exists (select 1 from GXD_Expression e
        where r._refs_key = e._refs_key
        and e.hasimage = 1
        )
and not exists (select 1 from BIB_Workflow_Tag wt
        where r._refs_key = wt._refs_key
        and wt._tag_key = 53059151
        )
order by year, jnumid
)
(
select r.*, 'gel' as assaytype,
array_to_string(array_agg(distinct i._image_key),',') as images,
array_to_string(array_agg(distinct p._imagepane_key),',') as imagepanes
from refs_fchigh r, GXD_Assay a, IMG_Image i, IMG_ImagePane p
where r._refs_key = a._refs_key
and a._assaytype_key in (1,2,3,4,5,6,8,9)
and a._imagepane_key = p._imagepane_key
and p._image_key = i._image_key
and i.xDim is not NULL
group by 1,2,3,4,5
union
select r.*, 'insitu' as assaytype,
array_to_string(array_agg(distinct i._image_key),',') as images,
array_to_string(array_agg(distinct i._imagepane_key),',') as imagepanes
from refs_fchigh r, GXD_Assay a, GXD_Specimen g, GXD_ISResultImage_View i
where r._refs_key = a._refs_key
and a._assaytype_key in (1,2,3,4,5,6,8,9)
and a._assay_key = g._assay_key
and g._specimen_key = i._specimen_key
and i.xDim is not NULL
group by 1,2,3,4,5
)
order by year, jnumid, assaytype
''', 'auto')

sys.stdout.write('jnumid' + TAB)
sys.stdout.write('journal' + TAB)
sys.stdout.write('number of gel images' + TAB)
sys.stdout.write('number of gel image panes' + TAB)
sys.stdout.write('number of insitu images' + TAB)
sys.stdout.write('number of insitu image panes' + TAB)
sys.stdout.write('title' + CRT)

printJnum = False
printGel = False

for r in results:

        if printJnum == False:
                sys.stdout.write(r['jnumid'] + TAB)
                sys.stdout.write(r['journal'] + TAB)
                printJnum = True

        if r['assaytype'] == 'gel':
                sys.stdout.write(str(len(r['images'])) + TAB)
                sys.stdout.write(str(len(r['imagepanes'])) + TAB)
                printGel = True
                continue

        if printGel == False:
                sys.stdout.write('0' + TAB)
                sys.stdout.write('0' + TAB)

        sys.stdout.write(str(len(r['images'])) + TAB)
        sys.stdout.write(str(len(r['imagepanes'])) + TAB)
        sys.stdout.write(r['title'] + CRT)
        printJnum = False
        printGel = False

sys.stdout.flush()

