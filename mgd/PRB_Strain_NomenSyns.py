#!/usr/local/bin/python

'''
#
# PRB_Strain_NomenSyns.py
#
# Report:
#       Tab-delimited file of Strains w/ Nomenclature Synonyms
#
# Usage:
#       PRB_Strain_NomenSyns.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	11/14/2005
#	- TR 7247
#
'''
 
import sys
import os
import string
import mgi_utils
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


#
# Main
#

fp = reportlib.init(sys.argv[0], title = 'Strain Nomenclature Synonyms', outputdir = os.environ['QCOUTPUTDIR'])
fp.write(string.ljust('MGI id', 35))
fp.write(string.ljust('strain', 85))
fp.write('synonyms' + reportlib.CRT)
fp.write(string.ljust('------------------------------', 35))
fp.write(string.ljust('--------------------------------------------------------------------------------', 85))
fp.write('--------------------------------------------------' + reportlib.CRT)

db.sql('select s._Strain_key, strain = substring(s.strain,1,80), sy.synonym, a.accID ' + \
	'into #strains ' + \
	'from PRB_Strain s, MGI_Synonym sy, ACC_Accession a ' + \
	'where s._Strain_key = sy._Object_key ' + \
	'and sy._MGIType_key = 10 ' + \
	'and sy._SynonymType_key = 1001 ' + \
	'and s._Strain_key = a._Object_key ' + \
	'and a._MGIType_key = 10 ' + \
	'and a._LogicalDB_key = 1 '+ \
	'and a.preferred = 1', None)

syns = {}
results = db.sql('select _Strain_key, synonym from #strains', 'auto')
for r in results:
    key = r['_Strain_key']
    value = r['synonym']
    if not syns.has_key(key):
        syns[key] = []
    syns[key].append(value)

results = db.sql('select distinct _Strain_key, strain, accID from #strains order by strain', 'auto')
for r in results:
    fp.write(string.ljust(r['accID'], 35))
    fp.write(string.ljust(r['strain'], 85))
    fp.write(string.joinfields(syns[r['_Strain_key']], ',') + reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

