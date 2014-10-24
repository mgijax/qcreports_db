#!/usr/local/bin/python

'''
#
# HMD_SymbolDiffs.py 06/10/2005
#
# Report:
#       Tab-delimited file (originally an SQL report)
#
# Usage:
#       HMD_SymbolDiffs.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec   10/24/2014
#       - TR11750/postres complient
#
# lec	09/19/2014
#	- TR11652/convert to new MRK_Cluster tables
#
# lec	06/10/2005
#	- TR 6858
#
'''
 
import sys
import os
import string
import mgi_utils
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
        RADAR = ''
    else:
        import db
        RADAR = os.environ['RADAR_DBNAME'] + '..'
except:
    import db
    RADAR = os.environ['RADAR_DBNAME'] + '..'

CRT = reportlib.CRT
TAB = reportlib.TAB

mgiID = {}
egID = {}
synonym = {}
hstatus = {}

def runQueries(includeRiken):

    global mgID, egID, synonym, hstatus

    if includeRiken:
	riken = 'and m1.symbol like "%Rik"'
    else:
	riken = 'and m1.symbol not like "%Rik"'

    #
    # select mouse/humanql('drop table #refs', None)

    try:
    	db.sql('drop table #homology', None)
    except:
	pass

    db.sql('''
	select distinct 
               m1._Marker_key as m_Marker_key, 
	       substring(m1.symbol,1,30) as msymbol, 
	       substring(m1.name, 1, 40) as mname, 
               substring(upper(ms.status), 1, 1) as mstatus, 
               m2._Marker_key as h_Marker_key, 
	       substring(m2.symbol,1,30) as hsymbol, 
	       substring(m2.name, 1, 40) as hname, 
               m2.modification_date 
        into #homology 
        from MRK_Homology_Cache h1, 
             MRK_Homology_Cache h2, 
             MRK_Marker m1, MRK_Marker m2, MRK_Status ms 
        where m1._Organism_key = 1 
        and m1._Marker_Status_key = ms._Marker_Status_key 
        and m1._Marker_key = h1._Marker_key 
        and h1._Class_key = h2._Class_key 
        and h2._Organism_key = 2 
        and h2._Marker_key = m2._Marker_key 
        and m1.symbol != m2.symbol 
	''' + riken, None)

    db.sql('create index idx1 on #homology(m_Marker_key)', None)
    db.sql('create index idx2 on #homology(h_Marker_key)', None)

    #
    # select mouse MGI ids
    #

    results = db.sql('''
	select h.m_Marker_key, a.accID 
	from #homology h, ACC_Accession a 
	where h.m_Marker_key = a._Object_key 
	and a._MGITYpe_key = 2 
        and a._LogicalDB_key = 1 
        and a.prefixPart = 'MGI:' 
        and a.preferred = 1 
	''', 'auto')
    for r in results:
	mgiID[r['m_Marker_key']] = r['accID']

    results = db.sql('''
	 select h.m_Marker_key, a.accID 
	 from #homology h, ACC_Accession a 
	 where h.m_Marker_key = a._Object_key 
	 and a._MGITYpe_key = 2 
         and a._LogicalDB_key = 55 
	 ''', 'auto')
    for r in results:
	egID[r['m_Marker_key']] = r['accID']

    #
    # select mouse synonyms
    #

    results = db.sql('''
	select h.m_Marker_key, substring(s.synonym,1,50) as synonym
        from #homology h, MGI_Synonym s, MGI_SynonymType st 
        where h.m_Marker_key = s._Object_key 
        and s.synonym not like '%Rik' 
        and s.synonym not like 'MGC:%' 
        and s._SynonymType_key = st._SynonymType_key 
        and st.synonymType = 'exact' 
	''', 'auto')
    for r in results:
	key = r['m_Marker_key']
	value = r['synonym']
	if not synonym.has_key(key):
	    synonym[key] = []
	synonym[key].append(value)

    try:
    	db.sql('drop table #results', None)
    except:
	pass

    db.sql('''
	select h.*, e.status as hstatus
	into #results 
        from #homology h, %sDP_EntrezGene_Info e 
        where h.hsymbol = e.symbol and e.taxID = 9606 
        union 
        select h.*, '?' as hstatus
        from #homology h 
        where not exists (select 1 from %sDP_EntrezGene_Info e 
        where h.hsymbol = e.symbol and e.taxID = 9606)
	''' % (RADAR, RADAR), None)

def report1(fp, includeRiken = 0):

    if includeRiken:
	riken = 'excludes RIKEN'
    else:
	riken = 'RIKEN only'

    fp.write('MGI Symbols differing from Human Ortholog Symbols, ' + riken + ' (#1)' + CRT)
    fp.write('(sorted by modification date of human symbol, symbol status, mouse symbol)' + 2*CRT)

    fp.write(string.ljust('MGI Symbol', 32))
    fp.write(string.ljust('MGI Status', 12))
    fp.write(string.ljust('MGI Human Symbol', 32))
    fp.write(string.ljust('Human Status', 15))
    fp.write(string.ljust('MGI ID', 32))
    fp.write(string.ljust('MGI Name', 42))
    fp.write(string.ljust('EntrezGene ID', 32))
    fp.write(string.ljust('Human Name', 42))
    fp.write(string.ljust('MGI Synonym', 42))
    fp.write(CRT)
    fp.write(string.ljust('-' * 30, 32))
    fp.write(string.ljust('-' * 10, 12))
    fp.write(string.ljust('-' * 30, 32))
    fp.write(string.ljust('-' * 12, 15))
    fp.write(string.ljust('-' * 30, 32))
    fp.write(string.ljust('-' * 40, 42))
    fp.write(string.ljust('-' * 30, 32))
    fp.write(string.ljust('-' * 40, 42))
    fp.write(string.ljust('-' * 40, 42))
    fp.write(CRT)


    results = db.sql('select * from #results order by modification_date, hstatus desc, msymbol', 'auto')

    for r in results:
	key = r['m_Marker_key']

	fp.write(string.ljust(r['msymbol'], 32) + \
		 string.ljust(r['mstatus'], 12) + \
		 string.ljust(r['hsymbol'], 32) + \
		 string.ljust(r['hstatus'], 15) + \
		 string.ljust(mgiID[key], 32) + \
		 string.ljust(r['mname'], 42))

        if egID.has_key(key):
	    fp.write(string.ljust(egID[key], 32))
        else:
	    fp.write(string.ljust('', 32))

        fp.write(string.ljust(r['hname'], 42))

	if synonym.has_key(key):
	    fp.write(string.ljust(string.join(synonym[key],','), 32))

        fp.write(CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

def report2(fp, includeRiken):

    if includeRiken:
	riken = 'excludes RIKEN'
    else:
	riken = 'RIKEN only'

    fp.write('MGI Symbols differing from Human Ortholog Symbols, ' + riken + ' (#2)' + CRT)
    fp.write('(sorted by human status, mouse status, mouse symbol)' + 2*CRT)

    fp.write(string.ljust('MGI Symbol', 32))
    fp.write(string.ljust('MGI Status', 12))
    fp.write(string.ljust('MGI Human Symbol', 32))
    fp.write(string.ljust('Human Status', 15))
    fp.write(string.ljust('MGI Synonym', 42))
    fp.write(CRT)
    fp.write(string.ljust('-' * 30, 32))
    fp.write(string.ljust('-' * 10, 12))
    fp.write(string.ljust('-' * 30, 32))
    fp.write(string.ljust('-' * 12, 15))
    fp.write(string.ljust('-' * 40, 42))
    fp.write(CRT)


    results = db.sql('select * from #results order by hstatus desc, mstatus desc, msymbol', 'auto')

    for r in results:
	key = r['m_Marker_key']

	fp.write(string.ljust(r['msymbol'], 32) + \
		 string.ljust(r['mstatus'], 12) + \
		 string.ljust(r['hsymbol'], 32) + \
		 string.ljust(r['hstatus'], 15))

	if synonym.has_key(key):
	    fp.write(string.ljust(string.join(synonym[key],','), 32))

        fp.write(CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

#
# Main
#

fp1 = reportlib.init('HMD_SymbolDiffs1', outputdir = os.environ['QCOUTPUTDIR'])
runQueries(includeRiken = 0)
report1(fp1, includeRiken = 0)
reportlib.finish_nonps(fp1)

fp3 = reportlib.init('HMD_SymbolDiffs3', outputdir = os.environ['QCOUTPUTDIR'])
runQueries(includeRiken = 1)
report1(fp3, includeRiken = 1)
reportlib.finish_nonps(fp3)

