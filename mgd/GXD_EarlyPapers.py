#!/usr/local/bin/python

'''
#
# TR 8343
#
# Report:
#
# The earliest paper for genes with 40 or more index records where the
# earliest paper has not been full coded.
#
# Usage:
#       GXD_EarlyPapers.py
#
# Notes:
#
# History:
#
# dbm	06/18/2007
#	- new
#
'''

import sys
import os
import string
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Popular genes whose (approximate) first paper has not been full coded', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(2*CRT)

fp.write(string.ljust('Gene', 20))
fp.write(SPACE)
fp.write(string.ljust('Index', 8))
fp.write(SPACE)
fp.write(string.ljust(' ', 10))
fp.write(SPACE)
fp.write(string.ljust('Priority', 10))
fp.write(SPACE)
fp.write(string.ljust(' ', 255))
fp.write(CRT)

fp.write(string.ljust('Symbol', 20))
fp.write(SPACE)
fp.write(string.ljust('Records', 8))
fp.write(SPACE)
fp.write(string.ljust('J Number', 10))
fp.write(SPACE)
fp.write(string.ljust('Score', 10))
fp.write(SPACE)
fp.write(string.ljust('Short Citation', 255))
fp.write(CRT)

fp.write(20*'-')
fp.write(SPACE)
fp.write(8*'-')
fp.write(SPACE)
fp.write(10*'-')
fp.write(SPACE)
fp.write(10*'-')
fp.write(SPACE)
fp.write(255*'-')
fp.write(CRT)

#
# Get the number of index records for each gene.
#
db.sql('''
       select _Marker_key, count(*) as idx_count
       into #counts 
       from GXD_Index 
       group by _Marker_key 
       having count(*) >= 40
       ''', None)

#
# Get the marker and reference keys for each gene identified in the
# first query.
#
db.sql('''
	select _Marker_key, _Refs_key 
        into #markerref 
        from GXD_Index gi 
        where exists (select 1 from #counts c 
                     where gi._Marker_key = c._Marker_key)
	''', None)

db.sql('create index markerref_idx1 on #markerref(_Marker_key)', None)
db.sql('create index markerref_idx2 on #markerref(_Refs_key)', None)

#
# Get the additional details for the report for each gene and each paper
# that has not been full coded.  In order to identify the earliest paper
# for a gene, a sort field is generated for each row that contains the year
# and J number (separated by a space).  This is used in the last query to
# get the earliest paper.
#
db.sql('''
	select mr._Marker_key, giv.symbol, giv.jnumID, 
              gi._Priority_key, vt.term, giv.short_citation, 
              str(br.year) + ' ' + giv.jnumID as sort_field
       into #details 
       from #markerref mr, GXD_Index gi, GXD_Index_View giv, VOC_Term vt, 
            BIB_Refs br 
       where mr._Marker_key = gi._Marker_key and 
             mr._Refs_key = gi._Refs_key and 
             gi._Index_key = giv._Index_key and 
             gi._Priority_key = vt._Term_key and 
             vt._Vocab_key = 11 and 
             gi._Refs_key = br._Refs_key and 
             not exists (select 1 from GXD_Assay ga 
                         where mr._Marker_key = ga._Marker_key and 
                               mr._Refs_key = ga._Refs_key)
	''', None)

#
# For each gene from the prior query, determine the minimum sort field
# (year and J number).  This sort field should match the sort field of
# the earliest paper in the prior query.
#
db.sql('''
	select mr._Marker_key, 
               min(str(br.year) + ' ' + bcc.jnumID) as sort_field
        into #firstref 
        from #markerref mr, BIB_Refs br, BIB_Citation_Cache bcc 
        where mr._Refs_key = br._Refs_key and 
              mr._Refs_key = bcc._Refs_key 
        group by mr._Marker_key 
        order by mr._Marker_key
	''', None)

#
# Get the fields for the report, using the sort field to idenify the
# earliest paper for each gene.
#
results = db.sql('''
	select d.symbol, c.idx_count, d.jnumID, d.term, 
               d.short_citation 
        from #details d, #firstref fr, #counts c 
        where d._Marker_key = fr._Marker_key and 
              d.sort_field = fr.sort_field and 
              d._Marker_key = c._Marker_key 
        order by d._Priority_key, c.idx_count desc
	''', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 20))
    fp.write(SPACE)
    fp.write(string.ljust(str(r['idx_count']), 8))
    fp.write(SPACE)
    fp.write(string.ljust(r['jnumID'], 10))
    fp.write(SPACE)
    fp.write(string.ljust(r['term'], 10))
    fp.write(SPACE)
    fp.write(string.ljust(r['short_citation'], 255))
    fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
