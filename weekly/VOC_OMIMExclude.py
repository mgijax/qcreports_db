#!/usr/local/bin/python

'''
#
# checkDOExcluded.py
#
# Compare the DO obo file with the OMIM.excluded file
#
# ${DATALOADSOUTPUT}/mgi/vocload/OMIM/OMIM.exclude
#
# Inputs:
#
# History:
#
'''

import sys 
import os
import db
import mgi_utils
import reportlib

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

excludeLookup = []
omimToDOLookup = {}

excludeFileName = os.environ['DATALOADSOUTPUT'] + '/mgi/vocload/OMIM/OMIM.exclude'
excludeFile = open(excludeFileName, 'r')

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('\nDO/OMIM ids that also exist in OMIM.exclude\n\n')

#
# exclude annotations if they use an OMIM id that belongs to > 1 DOI
#
for line in excludeFile.readlines():
	tokens = line[:-1].split('\t')
	excludeLookup.append('OMIM:' + tokens[0])
excludeFile.close()
#print excludeLookup

#
# omimToDOLookup
# omim id -> do id
#
results = db.sql('''
       select a1.accID as doID, a2.accID as omimID
       from ACC_Accession a1, VOC_Term t, ACC_Accession a2, ACC_Accession a3, VOC_Term t2
       where t._Vocab_key = 125
       and t._Term_key = a1._Object_key
       and a1._LogicalDB_key = 191
       and a1._Object_key = a2._Object_key
       and a2._LogicalDB_key = 15
       and a2.accID = a3.accID
       and a3._LogicalDB_key = 15
       and a3._Object_key = t2._Term_key
       ''', 'auto')
for r in results:
	key = r['omimID']
	value = r['doID']
	omimToDOLookup[key] = []
	omimToDOLookup[key].append(value)
#print omimToDOLookup

for omim in omimToDOLookup:
	if omim in excludeLookup:
		fp.write(omim + TAB)
		fp.write(omimToDOLookup[omim][0] + CRT)

reportlib.finish_nonps(fp)      # non-postscript file
