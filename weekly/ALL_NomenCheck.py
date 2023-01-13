
'''
#
# ALL_NomenCheck.py
#
# Report:
#       Weekly allele symbol and synonym check
#
# Usage:
#       ALL_NomenCheck.py
#
# History:
#
# 01/12/2023	sc
#	- WTS2-1091 New QC report for improper nomenclature in allele symbols and synonyms
#
'''

import sys 
import os
import string
import re
import reportlib
import mgi_utils
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

# regex to check for multiple < or > in symbol
pattern1 = '<' #r'<'
pattern2 = '>' #r'>'

synonymDict = {}
badAlleleSymbolList = []
badAlleleSynonymList = []

fp = reportlib.init(sys.argv[0], 'Alleles with Improper Nomenclature in Symbols and Synonyms', os.environ['QCOUTPUTDIR'])

results = db.sql('''
        select _Object_key as alleleKey, synonym
        from MGI_Synonym
        where _MGIType_key = 11
        ''', 'auto')

for r in results:
    key = r['alleleKey']
    if key not in synonymDict:
        synonymDict[key] = []
    synonymDict[key].append(r['synonym'])

results = db.sql('''select a.accid, aa._allele_key, aa.symbol
    from all_allele aa, acc_accession a
    where _allele_status_key != 847112 --deleted
    and aa._allele_key = a._object_key
    and a._mgitype_key = 11
    and a._logicaldb_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    order by aa.symbol''' , 'auto')

for r in results:
    alleleKey = r['_Allele_key']
    accid = r['accid']
    symbol = r['symbol']

    if len(re.findall(pattern1, symbol)) > 1 or len(re.findall(pattern2, symbol)) > 1:
        badAlleleSymbolList.append('%s%s%s' % (accid, TAB, symbol))

    if alleleKey in synonymDict:
        for synonym in synonymDict[alleleKey]:
            if len(re.findall(pattern1, synonym)) > 1 or len(re.findall(pattern2, synonym)) > 1:
                badAlleleSynonymList.append('%s%s%s%s%s' % (accid, TAB, symbol, TAB, synonym))

fp.write('Alleles with Improper Nomenclature in Symbols%s' % CRT)
fp.write('-------------------------------------------------%s' % CRT)
fp.write(str.join(CRT, badAlleleSymbolList))
fp.write('%sTotal: %s' % (CRT, len(badAlleleSymbolList)))
fp.write('%s%s' % (CRT, CRT))

fp.write('Alleles with Improper Nomenclature in Synonyms%s' % CRT)
fp.write('-------------------------------------------------%s' % CRT)
fp.write(str.join(CRT, badAlleleSynonymList))
fp.write('%sTotal: %s' % (CRT, len(badAlleleSynonymList)))
reportlib.finish_nonps(fp)	# non-postscript file
