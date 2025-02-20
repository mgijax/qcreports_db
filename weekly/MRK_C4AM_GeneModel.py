
'''
#
#	MRK_C4AM_GeneModel.py
#
# Report:
#       Weekly report of markers with curated coordinates associated with gene models
#
# Collection = 131,256,257
# AND
# Gene Model association exists for:  Ensembl Reg Gene Model, NCBI Gene Model, VISTA Gene Model, Ensembl Gene Model
#
# -- what is the difference between colleciton 131/MGI & 256/MGI Curation
# -- obsolete: where mcf._CreatedBy_key = 1523 /*mrk_coordload*/
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
import reportlib
import db

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'Markers with C4AM Coordinates and Gene Models', os.environ['QCOUTPUTDIR'])
fp.write('Marker ID%sCollection%sMarker Symbol%sGene Model IDs%s' % (TAB, TAB, TAB, CRT))

# curated via mrkcoordload
results = db.sql('''
    select mcf._Object_key as markerKey, a.accid as mgiID, m.symbol, mcc.name, gm.accid as gmID
    from MAP_Coord_Feature mcf, MAP_Coordinate mc, MAP_Coord_Collection mcc, ACC_Accession a, MRK_Marker m, ACC_Accession gm
    where mcf._Map_key = mc._Map_key
    and mc._Collection_key = mcc._Collection_key
    and mcf._Object_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and mcf._Object_key = m._Marker_key
    and a._Object_key = gm._Object_key
    and gm._mgitype_key = 2
    and gm._logicaldb_key in (223,222,60,59)
    order by symbol
    ''', 'auto')

for r in results:
    mgiID = r['mgiID']
    symbol = r['symbol']
    gmID = r['gmID']
    collection = r['name']
    fp.write('%s%s%s%s%s%s%s%s' % (mgiID, TAB, collection, TAB, symbol, TAB, gmID, CRT  ))

fp.write(CRT)
fp.write('Total: %s' % len(results))

reportlib.finish_nonps(fp)	# non-postscript file
