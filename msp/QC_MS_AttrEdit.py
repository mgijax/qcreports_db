#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Source Attribute Discrepencies
#       from QC_MS_AttrEdit.
#
# Usage:
#       QC_MS_AttrEdit.py OutputDir JobKey MGDDBinstance
#
# Notes:
#
# History:
#
# lec   03/17/2004
#       - created
#
'''
 
import sys 
import db
import string
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

outputDir = os.environ['OUTPUTDIR']
jobStreamKey = os.environ['JOBSTREAM']
mgdDB = os.environ['MGDDBNAME']

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Source Attribute Discrepency (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir)

fp.write("  A row in this report represents a Sequence's Anonymous Molecular Source attribute\n" + \
"  that has been curator-edited in MGI and whose incoming (new) value is not equal to\n" + \
"  its existing MGI value." + 2*CRT)

fp.write(string.ljust('Sequence ID', 16))
fp.write(string.ljust('Attribute Name', 19))
fp.write(string.ljust('MGI Value', 35))
fp.write(string.ljust('Incoming Value', 35))
fp.write(CRT)
fp.write(string.ljust('-----------', 16))
fp.write(string.ljust('--------------', 19))
fp.write(string.ljust('---------', 35))
fp.write(string.ljust('--------------', 35))
fp.write(CRT)

cmds = []

# strain, gender, cellLine, and tissue
cmds.append('select a.accID, qc.attrName, qc.incomingValue, resolvedValue = s.strain ' + \
	    'into #strains ' + \
	    'from QC_MS_AttrEdit qc, ' + \
	    '%s..SEQ_Source_Assoc sa, ' % (mgdDB) + \
	    '%s..ACC_Accession a, ' % (mgdDB) + \
	    '%s..PRB_Strain s ' % (mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc.source_key = sa._Source_key ' + \
	    'and sa._Sequence_key = a._Object_key ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and qc.attrName = "strain" ' + \
	    'and qc.attrValue = s._Strain_key ')

cmds.append('select a.accID, qc.attrName, qc.incomingValue, resolvedValue = s.tissue ' + \
	    'into #tissues ' + \
	    'from QC_MS_AttrEdit qc, ' + \
	    '%s..SEQ_Source_Assoc sa, ' % (mgdDB) + \
	    '%s..ACC_Accession a, ' % (mgdDB) + \
	    '%s..PRB_Tissue s ' % (mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc.source_key = sa._Source_key ' + \
	    'and sa._Sequence_key = a._Object_key ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and qc.attrName = "tissue" ' + \
	    'and qc.attrValue = s._Tissue_key ')

cmds.append('select a.accID, qc.attrName, qc.incomingValue, resolvedValue = s.term ' + \
	    'into #gender ' + \
	    'from QC_MS_AttrEdit qc, ' + \
	    '%s..SEQ_Source_Assoc sa, ' % (mgdDB) + \
	    '%s..ACC_Accession a, ' % (mgdDB) + \
	    '%s..VOC_Term s ' % (mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc.source_key = sa._Source_key ' + \
	    'and sa._Sequence_key = a._Object_key ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and qc.attrName = "gender" ' + \
	    'and qc.attrValue = s._Term_key ')

cmds.append('select a.accID, qc.attrName, qc.incomingValue, resolvedValue = s.term ' + \
	    'into #cellLine ' + \
	    'from QC_MS_AttrEdit qc, ' + \
	    '%s..SEQ_Source_Assoc sa, ' % (mgdDB) + \
	    '%s..ACC_Accession a, ' % (mgdDB) + \
	    '%s..VOC_Term s ' % (mgdDB) + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'and qc.source_key = sa._Source_key ' + \
	    'and sa._Sequence_key = a._Object_key ' + \
	    'and a._MGIType_key = 19 ' + \
	    'and qc.attrName = "cellLine" ' + \
	    'and qc.attrValue = s._Term_key ')

cmds.append('select accID, attrName, incomingValue, resolvedValue from #strains ' + \
            'union ' + \
	    'select accID, attrName, incomingValue, resolvedValue from #tissues ' + \
            'union ' + \
	    'select accID, attrName, incomingValue, resolvedValue from #gender ' + \
            'union ' + \
	    'select accID, attrName, incomingValue, resolvedValue from #cellLine ' + \
	    'order by accID, attrName')

results = db.sql(cmds, 'auto')

rows = 0
for r in results[-1]:
    fp.write(string.ljust(r['accID'], 16) + \
             string.ljust(r['attrName'], 19) + \
             string.ljust(r['resolvedValue'], 35) + \
             string.ljust(r['incomingValue'], 35) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

