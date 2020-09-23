
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

db.useOneConnection(1)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

# markers with gene model ids
#{markerKey:[gmId1, ...], ...}
geneModelDict = {}

# Organize result set by marker asmultiple gene models per marker
# {mgiID:[line], ...}
reportDict = {}

fp = reportlib.init(sys.argv[0], 'Markers with C4AM Coordinates and Gene Models', os.environ['QCOUTPUTDIR'])

# curated via mrkcoordload
db.sql('''select mcf._Object_key as markerKey, mcf.strand, mcf.startCoordinate, mcf.endCoordinate, c.chromosome, a.accid as mgiID, m.symbol, mt.name as markerType, t.term as featureType
    into temporary table curated
    from  MAP_Coord_Feature mcf, MAP_Coordinate mc, MAP_Coord_Collection mcc, MRK_Chromosome c, 
        ACC_Accession a, MRK_Marker m, MRK_Types mt, VOC_Annot va, VOC_Term t
    where mcf._CreatedBy_key = 1523 /*mrk_coordload*/
    and mcf._Map_key = mc._Map_key
    and mc._Collection_key = mcc._Collection_key
    and mc._Object_key = c._Chromosome_key
    and mcc._Collection_key = 64 /* MGI */
    and mcf._Object_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and mcf._Object_key = m._Marker_key
    and m._Marker_Type_key in (1, 7) /* Gene or Pseudogene */
    and m._Marker_Type_key = mt._Marker_Type_key
    and m._Marker_key = va._Object_key
    and va._AnnotType_key = 1011
    and va._Term_key = t._Term_key
    order by m.symbol ''', None)

# get curated markers with gene models, NCBI, Ensembl
results1 = db.sql('''select a.accid as genemodelID, c.*
from ACC_Accession a, curated c
where a._Object_key = c.markerKey
and a._MGIType_key = 2
and a._LogicalDB_key in (59, 60)
order by symbol''', 'auto')

for r in results1:
    markerKey = r['markerKey']
    gmId = r['genemodelID']
    if markerKey not in geneModelDict:
        geneModelDict[markerKey] = []
    geneModelDict[markerKey].append(gmId)

results2 = db.sql('''select * from curated''')

fp.write('Marker ID%sMarker Symbol%sMarker Type%sFeature Type%sChromosome%sStart%sEnd%sStrand%sGene Model IDs%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT))

for r in results2:
    mgiID = r['mgiID']
    symbol = r['symbol']
    key = '%s|%s' % (mgiID, symbol)
    markerKey = r['markerKey']
    gmIDs = ''
    if markerKey in geneModelDict:
        gmIDs = ', '.join(geneModelDict[markerKey])
    markerType = r['markerType']
    featureType = r['featureType']
    chromosome = r['chromosome']
    start = r['startCoordinate']
    end = r['endCoordinate']
    strand = r['strand']
    if strand == None:
        strand = ''
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (mgiID, TAB, symbol, TAB, markerType, TAB, featureType, TAB, chromosome, TAB, start, TAB, end, TAB, strand, TAB, gmIDs, CRT))


fp.write(CRT)
fp.write('Total: %s' % len(results2))

db.useOneConnection(0)
reportlib.finish_nonps(fp)	# non-postscript file
