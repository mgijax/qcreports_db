
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
# sc    02/11/2021
#       TR13349 - B39 project. Update to use alliance direct homology
#
# lec   05/15/2015
#	- TR11652/convert to new MRK_Cluster tables/other changes per Monica
#
# lec   10/24/2014
#       - TR11750/postres complient
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
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

mgiID = {}
hstatus = {}

def runQueries(includeRiken):

    global mgID, hstatus

    if includeRiken:
        riken = 'and (m1.symbol like \'%Rik\' or m1.symbol like \'Gm%\')'
    else:
        riken = 'and m1.symbol not like \'%Rik\' and m1.symbol not like \'Gm%\''

    db.sql('drop table if exists homology', None)

    db.sql('''
        select distinct 
               m1._Marker_key as m_Marker_key, 
               substring(m1.symbol,1,30) as msymbol, 
               substring(upper(ms.status), 1, 1) as mstatus, 
               m2._Marker_key as h_Marker_key, 
               substring(m2.symbol,1,30) as hsymbol, 
               m1.modification_date,
               to_char(m1.modification_date, 'MM/dd/yyyy') as mdate
        into temporary table homology 
        from MRK_Cluster mc,
             MRK_ClusterMember h1, 
             MRK_ClusterMember h2, 
             MRK_Marker m1, MRK_Marker m2, MRK_Status ms 
        where mc._ClusterSource_key = 75885739
        and mc._Cluster_key = h1._Cluster_key
        and h1._Marker_key = m1._Marker_key 
        and m1._Organism_key = 1 
        and m1._Marker_Status_key = ms._Marker_Status_key 
        and h1._Cluster_key = h2._Cluster_key 
        and h2._Marker_key = m2._Marker_key 
        and m2._Organism_key = 2 
        and lower(m1.symbol) != lower(m2.symbol)
        ''' + riken, None)

    db.sql('create index homology_idx1 on homology(m_Marker_key)', None)
    db.sql('create index homology_idx2 on homology(h_Marker_key)', None)

    #
    # select mouse MGI ids
    #

    results = db.sql('''
        select h.m_Marker_key, a.accID 
        from homology h, ACC_Accession a 
        where h.m_Marker_key = a._Object_key 
        and a._MGITYpe_key = 2 
        and a._LogicalDB_key = 1 
        and a.prefixPart = 'MGI:' 
        and a.preferred = 1 
        ''', 'auto')
    for r in results:
        mgiID[r['m_Marker_key']] = r['accID']

    db.sql('drop table if exists results', None)

    db.sql('''
        select h.*, e.status as hstatus
        into temporary table results 
        from homology h, radar.DP_EntrezGene_Info e 
        where h.hsymbol = e.symbol and e.taxID = 9606 
        union 
        select h.*, '?' as hstatus
        from homology h 
        where not exists (select 1 from radar.DP_EntrezGene_Info e 
        where h.hsymbol = e.symbol and e.taxID = 9606)
        ''', None)

def report1(fp, includeRiken = 0):

    if includeRiken:
        riken = 'RIKEN and Gene Models only'
    else:
        riken = 'excludes RIKEN and Gene Models'

    fp.write('MGI Symbols differing from Human Ortholog Symbols, ' + riken + ' (#1)' + CRT)
    fp.write('(sorted by modification date of human symbol, symbol status, mouse symbol)' + 2*CRT)

    fp.write(str.ljust('MGI Symbol', 32))
    fp.write(str.ljust('MGI Status', 12))
    fp.write(str.ljust('MGI Human Symbol', 32))
    fp.write(str.ljust('Date', 12))
    fp.write(str.ljust('Human Status', 15))
    fp.write(str.ljust('MGI ID', 32))
    fp.write(CRT)
    fp.write(str.ljust('-' * 30, 32))
    fp.write(str.ljust('-' * 10, 12))
    fp.write(str.ljust('-' * 30, 32))
    fp.write(str.ljust('-' * 10, 12))
    fp.write(str.ljust('-' * 12, 15))
    fp.write(str.ljust('-' * 30, 32))
    fp.write(CRT)


    results = db.sql('select * from results order by modification_date desc, hstatus desc, msymbol', 'auto')

    for r in results:
        key = r['m_Marker_key']

        fp.write(str.ljust(r['msymbol'], 32) + \
                 str.ljust(r['mstatus'], 12) + \
                 str.ljust(r['hsymbol'], 32) + \
                 str.ljust(r['mdate'], 12) + \
                 str.ljust(r['hstatus'], 15) + \
                 str.ljust(mgiID[key], 32))

        fp.write(CRT)

    fp.write('\n(%d rows affected)\n' % (len(results)))

def report2(fp, includeRiken):

    if includeRiken:
        riken = 'RIKEN and Gene Models only'
    else:
        riken = 'excludes RIKEN and Gene Models'

    fp.write('MGI Symbols differing from Human Ortholog Symbols, ' + riken + ' (#2)' + CRT)
    fp.write('(sorted by human status, mouse status, mouse symbol)' + 2*CRT)

    fp.write(str.ljust('MGI Symbol', 32))
    fp.write(str.ljust('MGI Status', 12))
    fp.write(str.ljust('MGI Human Symbol', 32))
    fp.write(str.ljust('Human Status', 15))
    fp.write(CRT)
    fp.write(str.ljust('-' * 30, 32))
    fp.write(str.ljust('-' * 10, 12))
    fp.write(str.ljust('-' * 30, 32))
    fp.write(str.ljust('-' * 12, 15))
    fp.write(CRT)


    results = db.sql('select * from results order by hstatus desc, mstatus desc, msymbol', 'auto')

    for r in results:
        key = r['m_Marker_key']

        fp.write(str.ljust(r['msymbol'], 32) + \
                 str.ljust(r['mstatus'], 12) + \
                 str.ljust(r['hsymbol'], 32) + \
                 str.ljust(r['hstatus'], 15))

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
