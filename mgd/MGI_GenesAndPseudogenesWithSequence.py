#!/usr/local/bin/python

'''
#
# MGI_Sequence.py
#
# Reports:
#
#       TR 8207
#
#       MGI Mouse Markers:
#       . of type "Gene" or pseudogene
#       . associated with at least one:  
#         NCBI Gene Model
#         Ensembl Gene Model
#         VEGA Gene Model
#         Any sequence
#
# History:
#
# 12/21/2011	lec
#	- convert to outer join
#
# jmason        20070320
#        - created based on TR 8207
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
TAB = reportlib.TAB

fpTAB = None

def init():
    #
    # initialize files
    #

    global fpTAB

    fpTAB = reportlib.init(sys.argv[0], 
        printHeading = None, 
        outputdir = os.environ['QCOUTPUTDIR'])

    printHeaderTAB()

def writeTAB(r):
    #
    # write record to tab-delimited file
    #

    # print marker records in tab-delimited format

    order = [
        r['mgiID'], 
        r['symbol'], 
        r['markerType'], 
        r['chr'], 
        r['startCoord'], 
        r['endCoord'], 
        r['strand'], 
        r['sequenceType'], 
        r['sequenceProvider']
    ]
    s = TAB.join(map(str,order))

    s += CRT

    return s

def printHeaderTAB():
    #
    # write record to tab-delimited file
    #

    fpTAB.write('# MGI - Genes and Pseudogenes with a Sequence' + CRT)
    fpTAB.write('# MGI ID' + TAB)
    fpTAB.write('Symbol' + TAB)
    fpTAB.write('Type' + TAB)
    fpTAB.write('Chr' + TAB)
    fpTAB.write('Start' + TAB)
    fpTAB.write('End' + TAB)
    fpTAB.write('Strand' + TAB)
    fpTAB.write('SeqType' + TAB)
    fpTAB.write('SeqProvider' + CRT)

def process():
    #
    # process data
    #

    #
    # Get all genes and pseudogenes that have a sequence of some kind
    # (representative sequence is good, but any sequence will do)
    #

    results = db.sql("""
            select  
            m._Marker_key, 
            a.accID as mgiID,
            m.symbol as symbol,
            m.chromosome as chr,
            mt.name as markerType,
            vt.term as sequenceType,
            vt2.term as sequenceProvider,
            mlc.startCoordinate as startCoord,
            mlc.endCoordinate as endCoord,
            mlc.strand as strand
            from
                ACC_Accession a,
                MRK_Marker m
		LEFT OUTER JOIN MRK_Location_Cache mlc on (m._Marker_key = mlc._Marker_key),
                MRK_Types mt,
                SEQ_Marker_Cache smc,
                VOC_Term vt,
                VOC_Term vt2
            where m._Organism_key = 1   -- Use the mouse as the organism
            and a._MGItype_key = 2      -- MGI Type key of type 'Marker'
            and a._Logicaldb_key = 1    -- Use the MGI Database
            and a.preferred = 1         -- Use the preferred marker ID
            and m._Marker_key = a._Object_key   -- Join on the Marker Primary Key
            and m._Marker_Status_key in (1,3)   -- Status of official or interim
            and m._Marker_Type_key = mt._Marker_Type_key
            and m._Marker_Type_key in (1,7)
            and m._Marker_key = smc._Marker_key
            and smc._Qualifier_key = vt._Term_key
            and smc._SequenceProvider_key = vt2._Term_key
            and smc._Sequence_key = (
            select min(c._Sequence_key) 
            from SEQ_Marker_Cache c 
            where c._Marker_key = smc._Marker_key
            )
            order by m.chromosome, mlc.startCoordinate
        """, 'auto')
    for r in results:
        fpTAB.write(writeTAB(r))
    fpTAB.write('Total: %s' % len(results))
    reportlib.finish_nonps(fpTAB)        # non-postscript file

#
# Main
#

init()
process()
