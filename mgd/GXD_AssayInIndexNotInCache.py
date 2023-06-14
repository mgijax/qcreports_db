
'''
#
# TR 8820
#
# Report:
#
# Please see the body of TR8820 for details, the description is too long to list here.
# In a nutshell however, this is looking for all assays that exist in the GXD cache, that DO NOT exist in the 
# GXD index.
#
# Usage:
#       GXD_AssayInCacheNotInIndex.py
#
# Notes:
#
# History:
#
# sc 01/28/2014
#	TR11507 - exclude Nuclease S1 and RNase protection
#
# lec	03/24/2011
#	- TR 10642/add '%quantitative RT%' to exclusion list
#
# lec	09/24/2009
#	- TR 9858
#	- make sure header prints out
#	- need to select the comments = null records
#
# mhall	05/12/2009
#	- TR 8820- created
#
#
'''
 
import sys 
import os 
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Full coded references that contain indexed assays that have not been full coded' + CRT)
fp.write('excluded:' + CRT)
fp.write('     index records that contain only cDNA, primer extension, RNase protection or Nuclease S1 assays' + CRT)
fp.write('     index records that contain only age ''E?''' + CRT)
fp.write('     index records that have a note that contains: ' + CRT)
fp.write('     ''ot blot'', ''fraction'', ''reverse'', ''immunoprecip'', ''binding'', ''rocket'', ''quantitative RT''' + CRT)
fp.write(CRT)

# Create a temporary table with all of the valid items from GXD_Index
# We specifically dont want anything with certain types of comments.

db.sql('''
select gi.*, bcc.jnumID, vt.term, gis._IndexAssay_key, gis._StageID_key, m.symbol
into temporary table validIndexItems
from GXD_Index gi, GXD_Index_Stages gis, BIB_Citation_Cache bcc, VOC_Term vt, MRK_Marker m
where gi._Index_key = gis._Index_key
and gi._Refs_key = bcc._Refs_key
and gis._IndexAssay_key = vt._Term_key
and gi._Marker_key = m._Marker_key
and lower(gi.comments) not like '%ot blot%'
and lower(gi.comments) not like '%fraction%'
and lower(gi.comments) not like '%reverse%'
and lower(gi.comments) not like '%immunoprecip%'
and lower(gi.comments) not like '%rocket%'
and lower(gi.comments) not like '%binding%'
and lower(gi.comments) not like '%quantitative RT%'
union
select gi.*, bcc.jnumID, vt.term, gis._IndexAssay_key, gis._StageID_key, m.symbol
from GXD_Index gi, GXD_Index_Stages gis, BIB_Citation_Cache bcc, VOC_Term vt, MRK_Marker m
where gi._Index_key = gis._Index_key
and gi._Refs_key = bcc._Refs_key
and gis._IndexAssay_key = vt._Term_key
and gi._Marker_key = m._Marker_key
and gi.comments is null
''', None)

db.sql('create index idx1 on validIndexItems(_Index_key)', None)
db.sql('create index idx2 on validIndexItems(_IndexAssay_key)', None)
db.sql('create index idx3 on validIndexItems(_StageID_key)', None)
db.sql('create index idx4 on validIndexItems(_Refs_key)', None)
db.sql('create index idx5 on validIndexItems(_Marker_key)', None)

db.sql('''
select distinct _Refs_key, _Marker_key, _AssayType_key
into temporary table tmp_gxd_expression
from GXD_Expression
where _AssayType_key not in (10,11)
''', None)

db.sql('create index idx6 on tmp_gxd_expression(_Refs_key)', None)
db.sql('create index idx7 on tmp_gxd_expression(_Marker_key)', None)
db.sql('create index idx8 on tmp_gxd_expression(_AssayType_key)', None)

# Match these types against the items in GXD_Expression versus its comparable types.
# Please note we dont bring back ANY matches to the "E?" stage.

results = db.sql('''
(
select jnumID, term as AssayType, symbol 
from validIndexItems gi
where gi._IndexAssay_key in (74718, 74720) and gi._StageID_key != 74769 
and exists (select 1 from tmp_gxd_expression ge 
        where gi._Refs_key = ge._Refs_key and gi._Marker_key = ge._Marker_key)
and not exists (select 1 from tmp_gxd_expression ga 
        where gi._Refs_key = ga._Refs_key 
and gi._Marker_key = ga._Marker_key and ga._AssayType_key = 1)

union
select distinct jnumID, term as AssayType, symbol 
from validIndexItems gi
where gi._IndexAssay_key = 74722 and gi._StageID_key != 74769
and exists (select 1 from tmp_gxd_expression ge 
        where gi._Refs_key = ge._Refs_key and gi._Marker_key = ge._Marker_key)
and not exists (select 1 from tmp_gxd_expression ga 
        where gi._Refs_key = ga._Refs_key 
and gi._Marker_key = ga._Marker_key and ga._AssayType_key = 2)

union
select distinct jnumID, term as AssayType, symbol 
from validIndexItems gi
where gi._IndexAssay_key = 74724 and gi._StageID_key != 74769 
and exists (select 1 from tmp_gxd_expression ge 
        where gi._Refs_key = ge._Refs_key and gi._Marker_key = ge._Marker_key)
and not exists (select 1 from tmp_gxd_expression ga 
        where gi._Refs_key = ga._Refs_key 
and gi._Marker_key = ga._Marker_key and ga._AssayType_key = 5)

union
select distinct jnumID, term as AssayType, symbol 
from validIndexItems gi
where gi._IndexAssay_key in (74717, 74719) and gi._StageID_key != 74769 
and exists (select 1 from tmp_gxd_expression ge 
        where gi._Refs_key = ge._Refs_key and gi._Marker_key = ge._Marker_key)
and not exists (select 1 from tmp_gxd_expression ga 
        where gi._Refs_key = ga._Refs_key 
and gi._Marker_key = ga._Marker_key and ga._AssayType_key = 6)

union
select distinct jnumID, term as AssayType, symbol 
from validIndexItems gi
where gi._IndexAssay_key = 74723 and gi._StageID_key != 74769  
and exists (select 1 from tmp_gxd_expression ge 
        where gi._Refs_key = ge._Refs_key and gi._Marker_key = ge._Marker_key)
and not exists (select 1 from tmp_gxd_expression ga 
        where gi._Refs_key = ga._Refs_key 
and gi._Marker_key = ga._Marker_key and ga._AssayType_key = 8)

union
select distinct jnumID, term as AssayType, symbol 
from validIndexItems gi
where gi._IndexAssay_key = 74721 and gi._StageID_key != 74769  
and exists (select 1 from tmp_gxd_expression ge 
        where gi._Refs_key = ge._Refs_key and gi._Marker_key = ge._Marker_key)
and not exists (select 1 from tmp_gxd_expression ga 
        where gi._Refs_key = ga._Refs_key 
and gi._Marker_key = ga._Marker_key and ga._AssayType_key = 9)
)

order by jnumID''', 'auto')

for item in results:
        fp.write(str.ljust(item['jnumID'], 30) + TAB)
        fp.write(str.ljust(item['AssayType'], 30) + TAB)
        fp.write(str.ljust(item['symbol'], 30) + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
