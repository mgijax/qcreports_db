#############################################################################
#
# TAL_check_superscript.py
#
# Usage: ${PYTHON} TAL_check_superscript.py
#
# Report:
#       Weekly report from the TAL input file that compares the allele 
#         supercript in the input file with the allele superscript in the 
#         allele nomen for all targeted alleles
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
#    from mgi_es_cell_current get columns
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
import re

db.useOneConnection(1)

CRT = reportlib.CRT
TAB = reportlib.TAB

superscriptRE = re.compile('.*tm[0-9]([a-z])')


fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Marker ID%sProject Name%sProject ID%sMCL%sAllele Superscript%sAllele Symbol (for the MCL from the database) %s' % (TAB, TAB, TAB, TAB, TAB, CRT))

fpIn = open(os.getenv('TAL_FILE'), 'r')

for line in fpIn.readlines():
    #print('\nLINE: %s ' % line)
    tokens = str.split(line, TAB)
    if len(tokens) < 8: # for blank lines
        continue
    mgiID = tokens[0]
    projectName = tokens[3]
    if projectName not in ['EUCOMM', 'EUCOMMTools', 'KOMP-CSD']:
        continue
    pid = tokens[4]
    if pid == '':
        #print('skipping: %s' % tokens)
        continue
    mcl = tokens[5]
    inSuperscript = tokens[7]
    if inSuperscript == '':
        inSuperscript = 'None'
    results = db.sql('''select a.symbol
                from all_cellline ac, all_allele a, all_allele_cellLine c
                where ac.cellline = '%s'
                and ac._cellline_key = c._mutantcellline_key
                and c._allele_key = a._allele_key''' % mcl, 'auto')

    alleleSymbol = 'None'  
    dbLetter = 'None'
    dbAlleleList = []
    found = 0
    # there could be zero, 1 or more alleles assoc w/mcl
    for r in results:
        dbAlleleList.append(r['symbol'])
    #print('mcl: %s dbAlleleList: %s inSuperscript: %s' % (mcl, dbAlleleList, inSuperscript))
    newDbAlleleList = [] # excludes derivatives   

    # look for inSuperscript in all symbols in dbAlleleList
    for dbSymbol in dbAlleleList:
        if str.find(dbSymbol, inSuperscript) != -1:
            found = 1
        
    if found:
        #print('found continuing')
        continue

    # now remove any derivative alleles from those that don't match, 
    # we don't want to report them
    for dbSymbol in dbAlleleList:
        res = superscriptRE.search(dbSymbol)
        if res:
            dbLetter = superscriptRE.search(dbSymbol).group(1)
        if dbLetter in ['a','e']:
            newDbAlleleList.append(dbSymbol)
    #print('mcl: %s newDbAlleleList: %s inSuperscript: %s' % (mcl, newDbAlleleList, inSuperscript))
    alleleSymbol  = ', '.join(newDbAlleleList)
    if alleleSymbol == '':
        alleleSymbol = 'None'
        
    if inSuperscript == 'None' and alleleSymbol == 'None':
        continue
        
    #print('writing to file')
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (mgiID, TAB, projectName, TAB, pid, TAB, mcl, TAB, inSuperscript, TAB, alleleSymbol, CRT))

fpIn.close()
reportlib.finish_nonps(fp)	# non-postscript file

db.useOneConnection(0)
