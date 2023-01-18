
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
badEmAlleleNameList = []
badTargAlleleNameList = []

fp = reportlib.init(sys.argv[0], 'Weekly Report for Alleles with Potentially Improper Nomenclature in Symbols, Synonyms and Names', os.environ['QCOUTPUTDIR'])

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

results = db.sql('''select distinct a.accid, aa._allele_key, aa.symbol, aa.name
    from all_allele aa, acc_accession a
    where aa._allele_type_key = 11927650
    and aa._allele_key = a._object_key
    and a._mgitype_key = 11
    and a._logicaldb_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and aa.name not like '%endonuclease-mediated mutation%' 
    and aa.name not like 'deletion%'
    and aa.name not like 'duplication%'
    and aa.name not like 'inversion%'
    and aa.name not like 'insertion%'
    order by symbol''', 'auto')

for r in results:
    badEmAlleleNameList.append('%s%s%s%s%s' % (r['accid'], TAB, r['symbol'], TAB, r['name'])
)

results = db.sql('''select distinct a.accid, aa._allele_key, aa.symbol, aa.name
    from all_allele aa, acc_accession a
    where aa._allele_type_key = 847116
    and aa._allele_key = a._object_key
    and a._mgitype_key = 11
    and a._logicaldb_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and aa.name not like '%targeted mutation%' 
    and aa.name not like 'deletion%'
    and aa.name not like 'duplication%'
    and aa.name not like 'inversion%'
    and aa.name not like 'insertion%' 
    order by symbol''', 'auto')

for r in results:
    badTargAlleleNameList.append('%s%s%s%s%s' % (r['accid'], TAB, r['symbol'], TAB, r['name'])
)
    
fp.write('Alleles with Improper Nomenclature in Symbols%s' % CRT)
fp.write('-------------------------------------------------%s' % CRT)
fp.write(str.join(CRT, badAlleleSymbolList))
fp.write('%sTotal: %s' % (CRT, len(badAlleleSymbolList)))
fp.write('%s%s' % (CRT, CRT))

fp.write('Alleles with Potentially Improper Nomenclature in Synonyms%s' % CRT)
fp.write('-------------------------------------------------%s' % CRT)
fp.write(str.join(CRT, badAlleleSynonymList))
fp.write('%sTotal: %s' % (CRT, len(badAlleleSynonymList)))
fp.write('%s%s' % (CRT, CRT))

fp.write('Endonuclease-mediated Alleles with Potentially Improper Nomenclature in Name%s' % CRT)
fp.write('-------------------------------------------------%s' % CRT)
fp.write(str.join(CRT, badEmAlleleNameList))
fp.write('%sTotal: %s' % (CRT, len(badEmAlleleNameList)))
fp.write('%s%s' % (CRT, CRT))

fp.write('Targeted Alleles with Potentially Improper Nomenclature in Name %s' % CRT)
fp.write('-------------------------------------------------%s' % CRT)
fp.write(str.join(CRT, badTargAlleleNameList))
fp.write('%sTotal: %s' % (CRT, len(badTargAlleleNameList)))

reportlib.finish_nonps(fp)	# non-postscript file
