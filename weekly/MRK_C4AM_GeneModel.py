#!/usr/local/bin/python

'''
#
#	MRK_C4AM_GeneModel.py
#
# Report:
#       Weekly report of markers with curated coordinates associated 
#	  with gene models
#
# Usage:
#       MRK_C4AM_GeneModel.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- use proper case for all table and column names e.g. 
#         use MRK_Marker not mrk_marker
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# sc	01/19/2017
#	- created TR12494
#
'''
 
import sys 
import os
import string
import reportlib
import db

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

# Organize result set by marker asmultiple gene models per marker
# {mgiID:[line], ...}
reportDict = {}

fp = reportlib.init(sys.argv[0], 'Markers with C4AM Coordinates and Gene Models', os.environ['QCOUTPUTDIR'])

# curated via mrkcoordload
db.sql('''select mcf._Object_key as markerKey, a.accid as mgiID, m.symbol
    into temporary table curated
    from  MAP_Coord_Feature mcf, MAP_Coordinate mc, MAP_Coord_Collection mcc, 
	ACC_Accession a, MRK_Marker m
    where mcf._CreatedBy_key = 1523 /*mrk_coordload*/
    and mcf._Map_key = mc._Map_key
    and mc._Collection_key = mcc._Collection_key
    and mcc._Collection_key = 64 /* MGI */
    and mcf._Object_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and mcf._Object_key = m._Marker_key''', None)

db.sql('create index idx1 on curated(markerKey)', None)

# get curated markers with gene models, NCBI, VEGA, Ensembl
results = db.sql('''select a.accid as genemodelID, c.* 
from ACC_Accession a, curated c
where a._Object_key = c.markerKey
and a._MGIType_key = 2
and a._LogicalDB_key in (59, 60, 85)
order by symbol''', 'auto') 

for r in results:
    mgiID = r['mgiID']
    symbol = r['symbol']
    gmID = r['genemodelID']
    key = '%s|%s' % (mgiID, symbol)
    if key not in reportDict:
	reportDict[key] = []
    reportDict[key].append(gmID)

fp.write('Marker ID%sMarker Symbol%sGene Model IDs%s' % (TAB, TAB, CRT))
for key in reportDict:
    gmIdList = reportDict[key]
    mgiID, symbol = string.split(key, '|')
    fp.write('%s%s%s%s%s%s' % (mgiID, TAB, symbol, TAB, string.join(gmIdList, ', '), CRT  ))

fp.write(CRT)
fp.write('Total: %s' % len(results))

reportlib.finish_nonps(fp)	# non-postscript file

