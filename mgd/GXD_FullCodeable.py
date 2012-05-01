#!/usr/local/bin/python

'''
#
# TR 6720 (report #1)
# TR 7887 (report #2)
# TR 8182 (report #3)
#
# Report:
#
# Usage:
#       GXD_FullCodeable.py
#
# History:
#
# 12/21/2011	lec
#	- convert to outer join
#
# lec	05/09/2011
#	- TR 10703; add medium priority records
#
# lec	09/23/2009
#	- TR 9806; add conditional column
#
# lec	10/22/2008
#	- TR 9336; add E? to report #2
#
# lec	07/24/2008
#	- TR 9149; include adult insitu (74770)
#
# dbm	06/06/2007
#	- modified report #1 to get high priority papers (TR 8235)
#	- modified report #1 to add OMIM annotation column (TR 8289)
#
# dbm	05/29/2007
#	- added report #3 (TR 8182)
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

# list of references that contain at least one E? annotation
eAnnot = []

def process():
    global eAnnot

    #
    # markers/papers where the paper is not excluded and
    # the marker does not have *any* coded papers.
    # only select medium or high priority papers
    # add in the E? annotation indicator.
    #

    db.sql('''
	select distinct g._Marker_key, g._Refs_key, g._Priority_key, 
          priority = t.term, conditional = t2.term
	into #refscodeable 
	from GXD_Index g, VOC_Term t, VOC_Term t2
	where g._Priority_key in (74715, 74714) 
	and g._Priority_key = t._Term_key 
	and g._ConditionalMutants_key = t2._Term_key
	and not exists (select 1 from GXD_Assay a where a._Marker_key = g._Marker_key) 
	''', None)

    db.sql('create index refscodeable_idx1 on #refscodeable(_Marker_key)', None)
    db.sql('create index refscodeable_idx2 on #refscodeable(_Refs_key)', None)

    #
    # count of total index records per reference
    #

    db.sql('''
	select g._Refs_key, idx_count = count(*) 
	into #indexcount 
	from GXD_Index g 
	group by g._Refs_key
	''', None)

    db.sql('create index indexcount_idx1 on #indexcount(_Refs_key)', None)

    #
    # those references that contain at least one E? annotation
    #

    results = db.sql('''
	select distinct g._Refs_key
	from #refscodeable g
        where exists (select 1 from GXD_Index i, GXD_Index_Stages gis 
            where g._Refs_key = i._Refs_key
	    and i._Index_key = gis._Index_key 
            and gis._StageID_key = 74769
            and gis._IndexAssay_key not in (74725,74728))
	''', 'auto')

    for r in results:
	eAnnot.append(r['_Refs_key'])

def report1(fp):

    fp.write(string.ljust('symbol', 35))
    fp.write(SPACE)
    fp.write(string.ljust('OMIM', 8))
    fp.write(SPACE)
    fp.write(string.ljust('index records', 20))
    fp.write(SPACE)
    fp.write(string.ljust('codeable papers', 25))
    fp.write(SPACE)
    fp.write(CRT)
    fp.write(string.ljust('------', 35))
    fp.write(SPACE)
    fp.write(string.ljust('----', 8))
    fp.write(SPACE)
    fp.write(string.ljust('-------------', 20))
    fp.write(SPACE)
    fp.write(string.ljust('-------------------------', 25))
    fp.write(SPACE)
    fp.write(CRT)

    #
    # all markers with high or medium priority papers that have not been full coded
    #

    db.sql('''
	select distinct gi._Marker_key 
        into #markers 
        from GXD_Index gi 
        where gi._Priority_key in (74714, 74715)
	and not exists (select 1 from GXD_Assay ga where ga._Marker_key = gi._Marker_key)
        ''', None)

    db.sql('create index markers_idx1 on #markers(_Marker_key)', None)

    #
    # all references for the markers of interest
    #

    jnums = {}	# key = Marker key, value = list of J numbers

    results = db.sql('''
	select gi._Marker_key, a.accID 
        from GXD_Index gi, #markers tm, ACC_Accession a 
        where gi._Priority_key in (74714, 74715) and 
            gi._Marker_key = tm._Marker_key and 
            gi._Refs_key = a._Object_key and 
            a._MGIType_key = 1 and 
            a._LogicalDB_key = 1 and 
            a.prefixPart = "J:"
	''', 'auto')

    for r in results:
        key = r['_Marker_key']
        value = r['accID']
        if not jnums.has_key(key):
	    jnums[key] = []
        jnums[key].append(value)

    #
    #
    # all markers with a human ortholog that has an OMIM annotation
    #

    omim = {}	# key = Marker key, value = 1

    results = db.sql('select distinct h1._Marker_key ' + \
                     'from MRK_Homology_Cache h1, MRK_Homology_Cache h2, ' + \
                          'MRK_Marker m1, MRK_Marker m2, ACC_Accession a, ' + \
                          '#markers tm ' + \
                     'where h1._Organism_key = 1 ' + \
                           'and h1._Class_key = h2._Class_key ' + \
                           'and h1._Marker_key = m1._Marker_key ' + \
                           'and h2._Marker_key = m2._Marker_key ' + \
                           'and m2._Marker_key = a._Object_key ' + \
                           'and a._MGIType_key = 2 ' + \
                           'and a._LogicalDB_key = 15 ' + \
                           'and m1._Marker_key = tm._Marker_key', 'auto')

    for r in results:
        omim[r['_Marker_key']] = 1

    #
    # number of index records for the markers of interest
    #

    results = db.sql('select m._Marker_key, m.symbol, idx_count = count(*) ' + \
                     'from GXD_Index gi, MRK_Marker m, #markers tm ' + \
                     'where gi._Marker_key = tm._Marker_key and ' + \
                           'gi._Marker_key = m._Marker_key ' + \
                     'group by m._Marker_key, m.symbol ' + \
                     'order by idx_count desc, m.symbol', 'auto')

    for r in results:
        fp.write(string.ljust(r['symbol'], 35))
        fp.write(SPACE)
        if omim.has_key(r['_Marker_key']):
            fp.write(string.ljust('Yes', 8))
        else:
            fp.write(string.ljust('No', 8))
        fp.write(SPACE)
        fp.write(string.ljust(str(r['idx_count']), 20))
        fp.write(SPACE)
        fp.write(string.join(jnums[r['_Marker_key']], ' '))
        fp.write(CRT)
	
    fp.write('\n(%d rows affected)\n' % (len(results)))

def report2(fp):

    fp.write ('note:  this report only contains references where ALL of its markers are not assay coded\n\n')

    fp.write(string.ljust('j number', 30))
    fp.write(SPACE)
    fp.write(string.ljust('index records', 20))
    fp.write(SPACE)
    fp.write(string.ljust('new genes', 20))
    fp.write(SPACE)
    fp.write(string.ljust('priority', 20))
    fp.write(SPACE)
    fp.write(string.ljust('E?', 4))
    fp.write(SPACE)
    fp.write(string.ljust('Conditional', 20))
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
    fp.write(string.ljust('----', 4))
    fp.write(SPACE)
    fp.write(string.ljust('-------------  ', 20))
    fp.write(SPACE)
    fp.write(CRT)

    #
    # count of new markers per reference
    #

    db.sql('''
	select g._Refs_key, mrk_count = count(*) 
	into #markercount 
	from #refscodeable g 
	group by g._Refs_key
	''', None)
    db.sql('create index markercount_idx1 on #markercount(_Refs_key)', None)

    #
    # we don't want a reference if it has any assays coded
    # that is, we only want references where all of their markers are not full coded
    #
    db.sql('''
	select g._Refs_key
	into #excluded
	from #refscodeable g, GXD_Assay a
	where g._Refs_key = a._Refs_key
	''', None)
    db.sql('create index excluded_idx1 on #excluded(_Refs_key)', None)

    results = db.sql('''
	select distinct r._Refs_key, a.accID, i.idx_count, m.mrk_count, r.priority, r.conditional 
	from #refscodeable r, #indexcount i, #markercount m, ACC_Accession a 
	where r._Refs_key = i._Refs_key 
	and r._Refs_key = m._Refs_key 
	and r._Refs_key = a._Object_key 
	and a._MGIType_key = 1 
	and a._LogicalDB_key = 1 
	and a.prefixPart = "J:" 
	and not exists (select 1 from #excluded d where r._Refs_key = d._Refs_key)
	order by r._Priority_key, m.mrk_count desc, a.numericPart desc
	''', 'auto')

    for r in results:

	fp.write(string.ljust(r['accID'], 30))
        fp.write(SPACE)
	fp.write(string.ljust(str(r['idx_count']), 20))
        fp.write(SPACE)
	fp.write(string.ljust(str(r['mrk_count']), 20))
        fp.write(SPACE)
	fp.write(string.ljust(r['priority'], 20))
        fp.write(SPACE)

	if r['_Refs_key'] in eAnnot:
	    fp.write(string.ljust('Yes', 4))
	else:
	    fp.write(string.ljust('No', 4))
        fp.write(SPACE)

	fp.write(string.ljust(r['conditional'], 20))
	fp.write(CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

def report3(fp):

    fp.write(string.ljust('j number', 30))
    fp.write(SPACE)
    fp.write(string.ljust('index records', 20))
    fp.write(SPACE)
    fp.write(string.ljust('new genes', 20))
    fp.write(SPACE)
    fp.write(string.ljust('priority', 20))
    fp.write(SPACE)
    fp.write(string.ljust('E?', 4))
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
    fp.write(string.ljust('----', 4))
    fp.write(SPACE)
    fp.write(CRT)

    #
    # get the number of new markers per reference
    #

    db.sql('''
	select i._Refs_key, mrk_count = count(*) 
        into #mrk_count 
        from GXD_Index i 
        where not exists (select 1 from GXD_Assay a where a._Marker_key = i._Marker_key) 
        group by i._Refs_key
	''', None)

    db.sql('create index mrk_count_idx1 on #mrk_count(_Refs_key)', None)

    #
    # get the priority
    # only select medium or high priority papers
    #

    db.sql('''
       select distinct i._Marker_key, i._Refs_key, i._Priority_key, priority = t.term 
           into #priority 
           from GXD_Index i, VOC_Term t 
	   where i._Priority_key in (74715, 74714) 
           and i._Priority_key = t._Term_key
	   ''', None)

    db.sql('create index priority_idx1 on #priority(_Refs_key)', None)

    #
    # get a list of references with assay type of northern, western, RT-PCR,
    # RNAse protection, or Nuclease S1 (aka blots)
    # no assay of immunohistochemistry, RNA in situ, or in situ reporter;
    #

    db.sql('''
       select distinct b._Refs_key 
       into #refs 
       from BIB_View b 
       where not exists (select 1 from GXD_Index i, GXD_Assay a 
                             where i._Refs_key = b._Refs_key 
                             and a._Refs_key   = i._Refs_key 
                             and a._Marker_key = i._Marker_key) 
       and exists (select 1 from GXD_Index i, GXD_Index_Stages s 
                             where  i._Refs_key = b._Refs_key 
                             and  s._index_key  = i._index_key 
                             and  s._indexAssay_key in (74722, 74723, 74724, 74726, 74727)) 
       and not exists (select 1 from GXD_Index i, GXD_Index_Stages s 
                             where  i._Refs_key = b._Refs_key 
                             and  s._index_key  = i._index_key 
                             and  s._indexAssay_key in (74717, 74718, 74719, 74720, 74721))
       ''', None)

    results = db.sql('''
	 select distinct r._Refs_key, a.accID, i.idx_count, m.mrk_count, p.priority 
	 from #refs r
	      LEFT OUTER JOIN #mrk_count m on (r._Refs_key = m._Refs_key),
	      #indexcount i, #priority p, ACC_Accession a 
	 where r._Refs_key = i._Refs_key 
	 and r._Refs_key = p._Refs_key 
         and r._Refs_key = a._Object_key 
         and a._MGIType_key = 1 
         and a._LogicalDB_key = 1 
         and a.prefixPart = "J:" 
	 order by p._Priority_key, m.mrk_count desc, i.idx_count desc
	 ''', 'auto')

    for r in results:
	if r['mrk_count'] == None:
		mrk_count = 0
        else:
		mrk_count = r['mrk_count']

	fp.write(string.ljust(r['accID'], 30))
        fp.write(SPACE)
	fp.write(string.ljust(str(r['idx_count']), 20))
        fp.write(SPACE)
	fp.write(string.ljust(str(mrk_count), 20))
        fp.write(SPACE)
	fp.write(string.ljust(r['priority'], 20))
        fp.write(SPACE)

	if r['_Refs_key'] in eAnnot:
	    fp.write('Yes')
	else:
	    fp.write('No')
	fp.write(CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

#
#  main
#

fp1 = reportlib.init(sys.argv[0], 'Markers that have no full coded data', outputdir = os.environ['QCOUTPUTDIR'])
fp2 = reportlib.init('GXD_FullCodeable2.py', 'Papers containing genes that are not in the full coded portion of the database', outputdir = os.environ['QCOUTPUTDIR'])
fp3 = reportlib.init('GXD_FullCodeable3.py', 'Blot-only papers that have not been fully coded', outputdir = os.environ['QCOUTPUTDIR'])

process()
report1(fp1)
report2(fp2)
report3(fp3)
reportlib.finish_nonps(fp1)
reportlib.finish_nonps(fp2)
reportlib.finish_nonps(fp3)

