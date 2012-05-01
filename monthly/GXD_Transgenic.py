#!/usr/local/bin/python

'''
#
# TR 9322 Assays that have annotations to genotypes using transgenic animals
#
# Report:
#
# Usage:
#       GXD_Transgenic.py
#
# History:
#
# lec	10/21/2008
#	- TR 9322
#
'''

import sys
import os
import string
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
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], 'Transgenic Genotype Check of the Expression Cache', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('Assays that have annotations to genotypes using transgenic animals\n')
fp.write('sorted by MGI ID of Assay')
fp.write(2*CRT)

fp.write(string.ljust('J#', 10))
fp.write(SPACE)
fp.write(string.ljust('MGI ID of Assay', 20))
fp.write(SPACE)
fp.write(string.ljust('Allele Symbol', 25))
fp.write(CRT)

fp.write(string.ljust('--------', 10))
fp.write(SPACE)
fp.write(string.ljust('--------------------', 20))
fp.write(SPACE)
fp.write(string.ljust('--------------------', 25))
fp.write(CRT)

#
# Assays
#
# undesirable allele types:
# Transgenic (random, gene discruption)
# Transgenic (random, expressed)
# Transgenic (Cre/Flp)
# Transgenic (reporter)
# Transgenic (Transposase)
#

db.sql('''
    select a._Refs_key, a._Assay_key, aa.symbol
    into #final
    from GXD_Assay a, GXD_Expression e, GXD_AlleleGenotype g, ALL_Allele aa
    where a._AssayType_key in (1,2,3,4,5,6,8,9)
    and a._Assay_key = e._Assay_key
    and e._Genotype_key = g._Genotype_key
    and g._Allele_key = aa._Allele_key
    and aa._Allele_Type_key in (847126, 847127, 847128, 847129, 2327160)
    ''', None)

db.sql('create index idx1 on #final(_Refs_key)', None)
db.sql('create index idx2 on #final(_Assay_key)', None)

results = db.sql('''
    select f.*, c.jnumID, mgiID = a.accID
    from #final f, BIB_Citation_Cache c, ACC_Accession a
    where f._Refs_key = c._Refs_key
    and f._Assay_key = a._Object_key
    and a._LogicalDB_key = 1
    and a._MGIType_key = 8
    order by mgiID
    ''', 'auto')

for r in results:
	fp.write(string.ljust(r['jnumID'], 10))
        fp.write(SPACE)
	fp.write(string.ljust(r['mgiID'], 20))
        fp.write(SPACE)
	fp.write(string.ljust(r['symbol'], 25) + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
db.useOneConnection(0)

