
'''
#
# Report:
#       This script produces a report of PIRSF superfamily ids 
#       loaded into MGD with duplicates names
#
# Usage:
#       'DuplicateTermNames.py
#
# Notes:
#
# History:
#
# mbw   10/03/2005
#       - created
#
'''
 
import os
import sys 
import string
import reportlib
import db

#db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#
outputDir=sys.argv[1]
jobKey=sys.argv[2]

fp = reportlib.init(sys.argv[0],  
                    'PIRSFLoad - Annotations loaded into MGD to markers other than genes (Job Stream %s)' % (jobKey), 
                    outputdir = outputDir, sqlLogging = 0)

fp.write('  A row in this report represents an annotation to a marker of type other than gene.' + 2*CRT)

fp.write(str.ljust('Marker type', 30))
fp.write(str.ljust('MGI Marker ID', 20))
fp.write(str.ljust('Symbol', 20))
fp.write(str.ljust('Superfamily ID', 15))
fp.write(str.ljust('Superfamily Name', 80))
fp.write(CRT)
fp.write(str.ljust('-----------------------------', 30))
fp.write(str.ljust('-------------------', 20))
fp.write(str.ljust('-------------------', 20))
fp.write(str.ljust('--------------', 15))
fp.write(str.ljust('-------------------------------------------------------------------------------', 80))
fp.write(CRT)

results = db.sql('''
        select mt.name, acc1.accID as markerid, m.symbol, acc2.accID as sfid, t.term 
        from MRK_Marker m, MRK_Types mt, ACC_Accession acc1, ACC_Accession acc2, VOC_Annot a, VOC_Term t 
        where a._AnnotType_key = 1007 
        and acc1._Object_key = a._Object_key 
        and acc1._MGIType_key = 2 
        and acc1._LogicalDB_key = 1 
        and acc1.preferred = 1 
        and m._Marker_key = a._Object_key 
        and mt._Marker_Type_key = m._Marker_Type_key 
        and m._Marker_Type_key != 1 
        and acc2._Object_key = a._Term_key 
        and acc2._MGIType_key = 13 
        and t._Term_key = a._Term_key 
        order by name
        ''', 'auto')

for r in results:
    fp.write(str.ljust(r['name'], 30) + \
             str.ljust(r['markerid'], 20) + \
             str.ljust(r['symbol'], 20) + \
             str.ljust(r['sfid'], 15) + \
             str.ljust(r['term'], 80) + \
             CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
