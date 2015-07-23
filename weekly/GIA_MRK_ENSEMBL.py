#!/usr/local/bin/python

'''
#
# TR 4970 (custom SQL TR 4338)
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
#
# Usage:
#       MRK_ENSEMBL.py
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# lec   02/09/2011
#	- this is similar to the report on public, but specific for Sophia
#	  and the ${MGD_DBUTILS}/bin/generateGIAssoc.csh product
#
# lec	08/26/2003
#	- added to reports_db product
#	- changed order of cM position and chromosome to be consistent
#	  with other Sequence reports.
#	- added outputdir, import os
#
# dbm   12/13/2002
#       - created
#
# NOTE: This report is a variation of the daily report with the same name.
#       It does not get copied to the FTP site and is only used by the
#       mgddbutilities product to generate the input file for the NIA
#       association load.
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

cmd = '''
	select a1.accID as mgiID, m.symbol, m.name, m.chromosome, o.cmoffset, a2.accID as ensemblID
        from ACC_Accession a1, ACC_Accession a2, MRK_Marker m, MRK_Offset o 
        where a1._Object_key = a2._Object_key 
            and a1._Object_key = m._Marker_key 
            and m._Marker_key = o._Marker_key 
            and a1._LogicalDB_key = 1 
            and a1._MGIType_key = 2 
            and a1.prefixPart = 'MGI:' 
            and a1.preferred = 1 
            and a2._LogicalDB_key = 60 
            and a2._MGIType_key = 2 
            and m._Marker_Type_key = 1 
            and o.source = 0 
        order by m.chromosome, m.symbol
	'''

results = db.sql(cmd, 'auto')

for r in results:
    fp.write(r['mgiID'] + TAB + r['symbol'] + TAB + r['name'] + TAB +
	     str(r['cmoffset']) + TAB +
             r['chromosome'] + TAB + 
             r['ensemblID'] + CRT)

reportlib.finish_nonps(fp)
