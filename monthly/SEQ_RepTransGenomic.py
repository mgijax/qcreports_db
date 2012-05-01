#!/usr/local/bin/python

'''
#
# SEQ_RepTransGenomic.py
#
# Report:
#	TR 6728
#
#       Tab-delimited file
#
#	Markers and their (optional) Representative Transcript and Genomic Sequences
#
#	MGI ID
#	Marker Type
#	Symbol
#	Rep Transcript ID
#	Rep Transcript Source
#	Chromosome
#	Rep Genomic ID
#	Rep Genomic Source
#	Start Coordinate
#	End Coordinate
#
# Usage:
#       SEQ_RepTransGenomic.py
#
# Used by:
#       Bob Sinclair (bobs)
#
# Notes:
#
# History:
#
# lec	04/12/2005
#	- new
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
    else:
        import db
except:
    import db


TAB = reportlib.TAB
CRT = reportlib.CRT

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

#
# Sequence Providers
#

provider = {}
results = db.sql('select _Term_key, term from VOC_Term where _Vocab_key = 25', 'auto')
for r in results:
    key = r['_Term_key']
    value = r['term']
    provider[key] = value

#
# Markers
#

db.sql('select m._Marker_key, m.symbol, m.chromosome, markerType = t.name, a.accID ' + \
	'into #markers ' + \
	'from MRK_Marker m, MRK_Types t, ACC_Accession a ' + \
	'where m._Organism_key = 1 ' + \
	'and m._Marker_Status_key  in (1,3) ' + \
	'and m._Marker_Type_key = t._Marker_Type_key ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ', None)

db.sql('create index idx1 on #markers(_Marker_key)', None)

#
# Representative Transcripts
#

transcript = {}
results = db.sql('select m._Marker_key, c.accID, c._SequenceProvider_key ' + \
	'from #markers m, SEQ_Marker_Cache c ' + \
	'where m._Marker_key = c._Marker_key ' + \
	'and c._Qualifier_key = 615420 ', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r
    transcript[key] = value

#
# Representative Genomic
#

coordinate = {}
results = db.sql('select m._Marker_key, c.accID, c._SequenceProvider_key, ' + \
	'startC = convert(int, d.startCoordinate), ' + \
	'endC = convert(int, d.endCoordinate) ' + \
	'from #markers m, SEQ_Marker_Cache c, SEQ_Coord_Cache d ' + \
	'where m._Marker_key = c._Marker_key ' + \
	'and c._Qualifier_key = 615419 ' + \
	'and c._Sequence_key = d._Sequence_key', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r
    coordinate[key] = value

#
# Process data
#

results = db.sql('select * from #markers order by symbol', 'auto')

for r in results:
    key = r['_Marker_key']

    fp.write(r['accID'] + TAB + \
	     r['markerType'] + TAB + \
	     r['symbol'] + TAB)

    if transcript.has_key(key):
	fp.write(transcript[key]['accID'] + TAB)
	p = provider[transcript[key]['_SequenceProvider_key']]
	fp.write(p + TAB)
    else:
	fp.write(TAB + TAB)

    fp.write(r['chromosome'] + TAB)

    if coordinate.has_key(key):
	fp.write(str(coordinate[key]['accID']) + TAB)
	p = provider[coordinate[key]['_SequenceProvider_key']]
	fp.write(p + TAB)
	fp.write(str(coordinate[key]['startC']) + TAB)
	fp.write(str(coordinate[key]['endC']) + CRT)
    else:
	fp.write(TAB + TAB + TAB + CRT)

reportlib.finish_nonps(fp)

