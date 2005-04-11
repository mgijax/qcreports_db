#!/usr/local/bin/python

'''
#
# TR 6720
#
# Report:
#
# Usage:
#       GXD_FullCodeable.py
#
# Notes:
#
# History:
#
# lec	04/11/2005
#	- converted GXD_FullCodeable.sql
#
'''

import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Genes that have not been full coded that have full codeable papers', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(string.ljust('symbol', 35))
fp.write(SPACE)
fp.write(string.ljust('index records', 20))
fp.write(SPACE)
fp.write(string.ljust('codeable papers', 20))
fp.write(SPACE)
fp.write(CRT)
fp.write(string.ljust('------', 35))
fp.write(SPACE)
fp.write(string.ljust('-------------', 20))
fp.write(SPACE)
fp.write(string.ljust('-------------  ', 20))
fp.write(SPACE)
fp.write(CRT)

# exclude any paper that contains an index stage E or A for the following assay:
# 	in situ protein (section)
#	in situ RNA (section)
#	in situ protein (whole mount)
#	in situ RNA (whole mount)
#	in situ reporter (knock in)
#
# exclude any paper that contains an index stage E for the following assay:
# 	northern blot
#	western blot
#	RT-PCR
#	RNase protection
#	nuclease S1
# 
# exclude any paper that has the following assay:
# 	cDNA clones 
#	primer extension

db.sql('select distinct gi._Refs_key ' + \
	'into #refsexcluded ' + \
	'from GXD_Index gi, GXD_Index_Stages gs ' + \
	'where gi._Index_key = gs._Index_key ' + \
	'and ((gs._IndexAssay_key in (74717, 74718, 74719, 74720, 74721) and gs._StageID_key in (74769, 74770)) ' + \
	'or  (gs._IndexAssay_key in (74722, 74723, 74724, 74726, 74727) and gs._StageID_key = 74769) ' + \
	'or  (gs._IndexAssay_key in (74725, 74728)))', None)

db.sql('create index idx1 on #refsexcluded(_Refs_key)', None)

db.sql('select distinct g._Marker_key, g._Refs_key ' + \
	'into #refscodeable ' + \
	'from GXD_Index g ' + \
	'where not exists (select 1 from #refsexcluded r where r._Refs_key = g._Refs_key) ' + \
	'and not exists (select 1 from GXD_Assay a where a._Marker_key = g._Marker_key) ', None)

db.sql('create index idx1 on #refscodeable(_Marker_key)', None)
db.sql('create index idx2 on #refscodeable(_Refs_key)', None)

#
# all papers in index
#

db.sql('select g._Marker_key, ref_count = count(*) ' + \
	'into #refsall ' + \
	'from GXD_Index g ' + \
	'group by g._Marker_key', None)

db.sql('create index idx1 on #refsall(_Marker_key)', None)

results = db.sql('select distinct r._Marker_key, a.accID from #refscodeable r, ACC_Accession a ' + \
	'where r._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "J:" ' + \
	'order by a.numericPart', 'auto')
jnums = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not jnums.has_key(key):
	jnums[key] = []
    jnums[key].append(value)

results = db.sql('select a._Marker_key, m.symbol, a.ref_count ' + \
	'from #refsall a, MRK_Marker m ' + \
	'where a._Marker_key = m._Marker_key ' + \
	'and exists (select 1 from #refscodeable r where a._Marker_key = r._Marker_key) ' + \
	'order by a.ref_count desc, m.symbol ', 'auto')

for r in results:
    fp.write(string.ljust(r['symbol'], 35))
    fp.write(SPACE)
    fp.write(string.ljust(str(r['ref_count']), 20))
    fp.write(SPACE)
    fp.write(string.join(jnums[r['_Marker_key']], ','))
    fp.write(CRT)
	
fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

