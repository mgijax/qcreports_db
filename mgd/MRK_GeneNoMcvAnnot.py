#!/usr/local/bin/python

'''
#
# MRK_GeneNomcvAnnot.py 06/07/10
#
# Report:
#       Markers of type gene with no Marker Category Vocab  annotations
#
# Usage:
#       geneNoMcvAnnot.py
#
# History:
#
# sc	01/11/2012
#	- TR10952 added interim as well as official markers
#
# sc	06/07/10
#	- created
#
'''
 
import sys 
import os
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

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Genes with no MCV Annotation%s%s' %(CRT, CRT))
fp.write('MGI ID%ssymbol%s' % (TAB, CRT) )
fp.write('-'*80 + CRT)

# select all official mouse markers of type gene without mcv annotations
cmds = []
cmds.append('''select _Marker_key, _Marker_Type_key, symbol
	into #noAnnot
	from MRK_Marker m
	where m._Marker_Status_key in (1,3)
	and _Organism_key = 1
	and _Marker_Type_key = 1
	and not exists(select 1
	from  VOC_Annot v
	where m._Marker_key = v._Object_key
	and v._AnnotType_key = 1011)''')

cmds.append('''select a.accid, n.symbol
	    from #noAnnot n, ACC_Accession a
	    where n._Marker_key = a._Object_key
	    and a._MGIType_key = 2
	    and a.preferred = 1
	    and a._LogicalDB_key = 1
	    and a.prefixPart = "MGI:"
	    order by n.symbol''')

results = db.sql(cmds, 'auto')

for r in results[1]:
    fp.write('%s%s%s%s' % (r['accid'], TAB, r['symbol'], CRT))
fp.write('\n(%d rows affected)\n' % (len(results[1])))
reportlib.finish_nonps(fp)
