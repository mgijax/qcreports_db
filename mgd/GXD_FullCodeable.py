#!/usr/local/bin/python

'''
#
# TR 6720 (report #1)
# TR 7887 (report #2)
#
# Report:
#
# Usage:
#       GXD_FullCodeable.py
#
# History:
#
# lec	09/07/2006
#	- added report #2 (TR 7887)
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

def process():

    #
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

    db.sql('select distinct gi._Refs_key ' + \
	'into #recsexcluded ' + \
	'from GXD_Index gi, GXD_Index_Stages gs ' + \
	'where gi._Index_key = gs._Index_key ' + \
	'and ((gs._IndexAssay_key in (74717, 74718, 74719, 74720, 74721) and gs._StageID_key in (74769, 74770)) ' + \
	'or  (gs._IndexAssay_key in (74722, 74723, 74724, 74726, 74727) and gs._StageID_key = 74769)) ', None)

    # 
    # exclude any paper that *only* has the following assay:
    # 	cDNA clones 
    #	primer extension

    db.sql('insert into #recsexcluded ' + \
	'select distinct gi._Refs_key ' + \
	'from GXD_Index gi, GXD_Index_Stages gs  ' + \
	'where gi._Index_key = gs._Index_key ' + \
	'and gs._IndexAssay_key in (74725, 74728) ' + \
	'and not exists (select 1 from GXD_Index_Stages gs2 ' + \
	'where gi._Index_key = gs2._Index_key ' + \
	'and gs2._IndexAssay_key not in (74725, 74728))', None)

    db.sql('create index idx1 on #recsexcluded(_Refs_key)', None)

    #
    # markers/papers where the paper is not excluded and
    # the marker does not have *any* coded papers.
    #

    db.sql('select distinct g._Marker_key, g._Refs_key, g._Priority_key, priority = t.term ' + \
	'into #refscodeable ' + \
	'from GXD_Index g, VOC_Term t ' + \
	'where g._Priority_key = t._Term_key ' + \
	'and not exists (select 1 from #recsexcluded r where r._Refs_key = g._Refs_key) ' + \
	'and not exists (select 1 from GXD_Assay a where a._Marker_key = g._Marker_key) ', None)

    db.sql('create index idx1 on #refscodeable(_Marker_key)', None)
    db.sql('create index idx2 on #refscodeable(_Refs_key)', None)

def report1(fp):

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

    #
    # all papers in index
    #

    db.sql('select g._Marker_key, ref_count = count(*) ' + \
	'into #refsall ' + \
	'from GXD_Index g ' + \
	'group by g._Marker_key', None)

    db.sql('create index idx1 on #refsall(_Marker_key)', None)

    #
    # resolve jnum
    #

    jnums = {}	# key = Marker key, value = list of J numbers

    results = db.sql('select distinct r._Marker_key, a.accID from #refscodeable r, ACC_Accession a ' + \
	'where r._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "J:" ' + \
	'order by a.numericPart', 'auto')
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
        fp.write(string.join(jnums[r['_Marker_key']], ' '))
        fp.write(CRT)
	
    fp.write('\n(%d rows affected)\n' % (len(results)))

def report2(fp):

    fp.write('This report excludes papers that have E? and adult in situ data.\n\n')

    fp.write(string.ljust('j number', 30))
    fp.write(SPACE)
    fp.write(string.ljust('index records', 20))
    fp.write(SPACE)
    fp.write(string.ljust('new genes', 20))
    fp.write(SPACE)
    fp.write(string.ljust('priority', 20))
    fp.write(SPACE)
    fp.write(CRT)
    fp.write(string.ljust('-------------', 30))
    fp.write(SPACE)
    fp.write(string.ljust('-------------', 20))
    fp.write(SPACE)
    fp.write(string.ljust('-------------  ', 20))
    fp.write(SPACE)
    fp.write(string.ljust('-------------  ', 20))
    fp.write(SPACE)
    fp.write(CRT)

    #
    # count of total index records per reference
    #

    db.sql('select g._Refs_key, idx_count = count(*) ' + \
	'into #indexcount ' + \
	'from GXD_Index g ' + \
	'group by g._Refs_key', None)

    db.sql('create index idx1 on #indexcount(_Refs_key)', None)

    #
    # count of new markers per reference
    #

    db.sql('select g._Refs_key, mrk_count = count(*) ' + \
	'into #markercount ' + \
	'from #refscodeable g ' + \
	'group by g._Refs_key', None)

    db.sql('create index idx1 on #markercount(_Refs_key)', None)

    results = db.sql('select distinct a.accID, i.idx_count, m.mrk_count, r.priority ' + \
	'from #refscodeable r, #indexcount i, #markercount m, ACC_Accession a ' + \
	'where r._Refs_key = i._Refs_key ' + \
	'and r._Refs_key = m._Refs_key ' + \
	'and r._Refs_key = a._Object_key ' + \
	'and a._MGIType_key = 1 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "J:" ' + \
	'order by r._Priority_key, m.mrk_count desc, a.numericPart desc', 'auto')

    for r in results:
	fp.write(string.ljust(r['accID'], 30))
        fp.write(SPACE)
	fp.write(string.ljust(str(r['idx_count']), 20))
        fp.write(SPACE)
	fp.write(string.ljust(str(r['mrk_count']), 20))
        fp.write(SPACE)
	fp.write(string.ljust(r['priority'], 20) + CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

#
#  main
#

fp1 = reportlib.init(sys.argv[0], 'Markers that have not been full coded that have full codeable papers', outputdir = os.environ['QCOUTPUTDIR'])
fp2 = reportlib.init('GXD_FullCodeable2.py', 'Papers containing genes that are not in the full coded portion of the database', outputdir = os.environ['QCOUTPUTDIR'])

process()
report1(fp1)
report2(fp2)
reportlib.trailer(fp1)
reportlib.finish_nonps(fp1)
reportlib.trailer(fp2)
reportlib.finish_nonps(fp2)

