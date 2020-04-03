
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
import db

db.setTrace()

#
# Main
#

fp = reportlib.init(sys.argv[0], title = 'Strain Nomenclature Synonyms', outputdir = os.environ['QCOUTPUTDIR'])
fp.write(str.ljust('MGI id', 35))
fp.write(str.ljust('strain', 85))
fp.write('synonyms' + reportlib.CRT)
fp.write(str.ljust('------------------------------', 35))
fp.write(str.ljust('--------------------------------------------------------------------------------', 85))
fp.write('--------------------------------------------------' + reportlib.CRT)

db.sql('''
        select s._Strain_key, substring(s.strain,1,80) as strain, sy.synonym, a.accID 
        into temporary table strains 
        from PRB_Strain s, MGI_Synonym sy, ACC_Accession a 
        where s._Strain_key = sy._Object_key 
        and sy._MGIType_key = 10 
        and sy._SynonymType_key = 1001 
        and s._Strain_key = a._Object_key 
        and a._MGIType_key = 10 
        and a._LogicalDB_key = 1 
        and a.preferred = 1
        ''', None)

syns = {}
results = db.sql('select _Strain_key, synonym from strains', 'auto')
for r in results:
    key = r['_Strain_key']
    value = r['synonym']
    if key not in syns:
        syns[key] = []
    syns[key].append(value)

results = db.sql('select distinct _Strain_key, strain, accID from strains order by strain', 'auto')
for r in results:
    fp.write(str.ljust(r['accID'], 35))
    fp.write(str.ljust(r['strain'], 85))
    fp.write(','.join(syns[r['_Strain_key']]) + reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
