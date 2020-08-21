
'''
#
# PRB_Strain.py 09/27/2001
#
# Report:
#       Tab-delimited file
#       All Strains
#
# Usage:
#       PRB_Strain.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	09/27/2001
#	- TR 2541
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

# Retrieve MGI Accession number

results = db.sql('''
        select distinct a._Object_key, a.accID 
        from ACC_Accession a 
        where a._MGIType_key = 10 
        and a._LogicalDB_key = 1 
        and a.prefixPart = 'MGI:' 
        and a.preferred = 1
        ''', 'auto')
mgiIDs = {}
for r in results:
        mgiIDs[r['_Object_key']] = r['accID']

# External Accession IDs

results = db.sql('''
        select distinct a._Object_key, a.accID 
        from ACC_Accession a 
        where a._LogicalDB_key != 1 
        and a._MGIType_key = 10 
        ''', 'auto')
externalIDs = {}
for r in results:
        if r['_Object_key'] in externalIDs:
                externalIDs[r['_Object_key']].append(r['accID'])
        else:
                externalIDs[r['_Object_key']] = []
                externalIDs[r['_Object_key']].append(r['accID'])

# Retrieve markers

results = db.sql('select _Strain_key, symbol from PRB_Strain_Marker_View where symbol is not null', 'auto')
markers = {}
for r in results:
        if r['_Strain_key'] in markers:
                markers[r['_Strain_key']].append(r['symbol'])
        else:
                markers[r['_Strain_key']] = []
                markers[r['_Strain_key']].append(r['symbol'])

# Retrieve synonyms

results = db.sql('select _Object_key, synonym from MGI_Synonym_Strain_View', 'auto')
syns = {}
for r in results:
        if r['_Object_key'] in syns:
                syns[r['_Object_key']].append(r['synonym'])
        else:
                syns[r['_Object_key']] = []
                syns[r['_Object_key']].append(r['synonym'])

# Retrieve all Strains

results = db.sql('select _Strain_key, strain, private from PRB_Strain order by strain', 'auto')
for r in results:
        if r['_Strain_key'] in mgiIDs:
                fp.write(mgiIDs[r['_Strain_key']] + reportlib.TAB)
        else:
                fp.write(reportlib.TAB)

        fp.write(r['strain'] + reportlib.TAB)

        if r['_Strain_key'] in markers:
                fp.write('|'.join(markers[r['_Strain_key']]) + reportlib.TAB)
        else:
                fp.write(reportlib.TAB)

        if r['_Strain_key'] in externalIDs:
                fp.write('|'.join(externalIDs[r['_Strain_key']]) + reportlib.TAB)
        else:
                fp.write(reportlib.TAB)

        if r['_Strain_key'] in syns:
                fp.write('|'.join(syns[r['_Strain_key']]) + reportlib.TAB)
        else:
                fp.write(reportlib.TAB)

        fp.write(repr(r['private']) + reportlib.CRT)

reportlib.finish_nonps(fp)
