
'''
#
# TR 8966
#
# Report:
#       Produce a tab-delimited report with the following output fields:
#
#       MGD ID
#       Gene Symbol
#       Gene Name
#       Chromosome
#       cM Position
#       Ensembl Gene ID
#	JNumber
#
# Usage:
#       MGI_ENSEMBL.py
#
# History:
#
# lec	05/08/2008
#	- TR 8966; Build 37
#	copied from TR4970
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

cmd = '''
      select a1.accID as mgiID, m.symbol, m.name, m.chromosome, m.cmOffset, a2.accID as seqID, a3.accID as jnum
      from ACC_Accession a1, ACC_Accession a2, MRK_Marker m, ACC_AccessionReference r, ACC_Accession a3 
      where a1._Object_key = a2._Object_key and 
            a1._Object_key = m._Marker_key and 
            a1._LogicalDB_key = 1 and 
            a1._MGIType_key = 2 and 
            a1.prefixPart = 'MGI:' and 
            a1.preferred = 1 and 
            a2._LogicalDB_key = 60 and 
            a2._MGIType_key = 2 and 
            m._Marker_Type_key = 1 and 
            a2._Accession_key = r._Accession_key and 
            r._Refs_key = a3._Object_key and 
            a3._LogicalDB_key = 1 and 
            a3._MGIType_key = 1 and 
            a3.prefixPart = 'J:' and 
            a3.preferred = 1 
      order by m.chromosome, m.symbol
      '''

results = db.sql(cmd, 'auto')

for r in results:
    fp.write(r['mgiID'] + TAB + 
             r['symbol'] + TAB + 
             r['name'] + TAB +
             str(r['cmOffset']) + TAB +
             r['chromosome'] + TAB + 
             r['seqID'] + TAB + \
             r['jnum'] + CRT)

reportlib.finish_nonps(fp)
