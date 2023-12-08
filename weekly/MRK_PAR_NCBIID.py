
'''
#
#	MRK_PAR_NCBIID.py
#
# Report:
#       Weekly report of cases where the NCBI ID is different between PARX/PARY PARtner_of marker pairs
#       Currently the NCBI assigns the same ID to both PAR markers. This report is to catch
#       partners that have different NCBI IDs which would only happen if NCBI changes its paradigm
#
# Usage:
#       MRK_PAR_NCBIID.py
#
#
# History:
#
# sc	04/05/2023
#	- created FL2b project - PAR Epic
#
'''
 
import sys 
import os
import reportlib
import db

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('#\n')
fp.write('# PARtner_NCBI_Discrepancy Report\n')
fp.write('# field 1: Marker1 ID\n')
fp.write('# field 2: Marker1 Symbol\n')
fp.write('# field 3: Marker1 NCBI ID\n')
fp.write('# field 4: Marker2 ID\n')
fp.write('# field 5: Marker2 Symbol\n')
fp.write('# field 6: Marker2 NCBI ID\n')
fp.write('#\n')

results = db.sql('''select  a3.accid as mgiID1, m1.symbol as symbol1, 
        a1.accid as ncbiId1, a4.accid as mgiID2, m2.symbol as symbol2, a2.accid as ncbiId2
    from mgi_relationship r, mrk_marker m1, mrk_marker m2, acc_accession a1, 
        acc_accession a2, acc_accession a3, acc_accession a4
    where _category_key = 1012
    and r._object_key_1 = m1._marker_key
    and m1._marker_key = a1._object_key
    and a1._mgitype_key = 2
    and a1._logicaldb_key = 55
    and a1.preferred = 1
    and r._object_key_2 = m2._marker_key
    and m2._marker_key = a2._object_key
    and a2._mgitype_key = 2
    and a2._logicaldb_key = 55
    and a2.preferred = 1
    and m1._marker_key = a3._object_key
    and a3._mgitype_key = 2
    and a3._logicaldb_key = 1
    and a3.preferred = 1
    and a3.prefixPart = 'MGI:'
    and m2._marker_key = a4._object_key
    and a4._mgitype_key = 2
    and a4._logicaldb_key = 1
    and a4.preferred = 1
    and a4.prefixPart = 'MGI:' 
    order by symbol1''', 'auto')

currentParRelationships = []
mismatchCt = 0
for r in results:
    ncbiId1 = r['ncbiId1']
    ncbiId2 = r['ncbiId2']
    if ncbiId1 != ncbiId2:
        mgiId1 = r['mgiID1']
        symbol1 = r['symbol1']
        mgiId2 = r['mgiID2']
        symbol2 = r['symbol2']
        if mgiId1 not in currentParRelationships and mgiId2 not in currentParRelationships:
            mismatchCt += 1
            currentParRelationships.append(mgiId1)
            currentParRelationships.append(mgiId2)
            fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (mgiId1, TAB, symbol1, TAB, ncbiId1, TAB, mgiId2, TAB, symbol2, TAB, ncbiId2, CRT))

fp.write(CRT)
fp.write('Total: %s' % mismatchCt)

reportlib.finish_nonps(fp)	# non-postscript file
