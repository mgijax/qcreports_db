#############################################################################
#
# TAL_multiple_project_ids.py
#
# Usage:
#       ${PYTHON} TAL_multiple_project_ids.py
#
# Report:
#       Weekly report from the TAL input file of Marker/Allele Superscripts with multiple Project IDs
#
# History:
#
# sc    10/03/2023
#       - moved from targetedalleleload
#
# sc	07/21/2023
#	- created FL2-451/WTS2-1167
#
# Notes:
#   from mgi_es_cell_current get columsns
#       1. Marker MGI ID
#       4. Project Name
#       5. Project ID
#       6. MCL
#       8. Allele Superscript
#############################################################################
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()
db.useOneConnection(1)

CRT = reportlib.CRT
TAB = reportlib.TAB

# {mgiID|superscript: [[projectName, pid, mcl], ...}
inputDict = {}

# the report in list format, that will be sorted then written to the report
outputList = []

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Marker ID%sProject Name%sProject ID%sMCL%sAllele Superscript%sAllele Symbol (for the MCL from the database) %s' % (TAB, TAB, TAB, TAB, TAB, CRT))

fpIn = open(os.getenv('TAL_FILE'), 'r')

for line in fpIn.readlines():
    tokens = str.split(line, TAB)
    if len(tokens) < 8: # for blank lines
        continue
    mgiID = tokens[0]
    projectName = tokens[3]
    if projectName not in ['EUCOMM', 'EUCOMMTools']:
        continue
    pid = tokens[4]
    if pid == '':
        continue
    mcl = tokens[5]
    superscript = tokens[7]
    key = '%s|%s' % (mgiID, superscript)
    value = [projectName, pid, mcl]
    if key not in inputDict:
        inputDict[key] = []
    inputDict[key].append(value)


for key in inputDict:
    pidList = []
    for value in inputDict[key]:
        pid = value[1]
        if pid not in pidList:
            pidList.append(pid)
    if len(pidList) > 1:
        for info in inputDict[key]:
            tokens = str.split(key, '|')
            mgiID = tokens[0]
            superscript = tokens[1]
            projectName = info[0]
            pid = info[1]
            mcl = info[2]
            alleleSymbol = 'None' 
            results = db.sql('''select a.symbol
                from all_cellline ac, all_allele a, all_allele_cellLine c
                where ac.cellline = '%s'
                and ac._cellline_key = c._mutantcellline_key
                and c._allele_key = a._allele_key''' % mcl, 'auto')
            if len(results):
                alleleSymbol = results[0]['symbol']
            outputList.append([mgiID, projectName, pid, mcl, superscript, alleleSymbol])

sortedOutput = sorted(outputList, key=lambda ol: (ol[0], ol[5], ol[3], ol[4]))

for lineList in sortedOutput:
        print('\t'.join(lineList))
        fp.write('%s%s' % ('\t'.join(lineList), CRT))

fpIn.close()
reportlib.finish_nonps(fp)	# non-postscript file

db.useOneConnection(0)

