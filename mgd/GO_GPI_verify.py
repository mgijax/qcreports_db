#!/usr/local/bin/python

'''
   'gene product' values that do not exist in the GPI file

'''

import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

gpiSet = ['PR', 'EMBL', 'ENSEMBL', 'RefSeq', 'VEGA']
gpiFileName = os.environ['PUBREPORTDIR'] + '/output/mgi.gpi'
gpiFile = open(gpiFileName, 'r')
gpiLookup = []

fp = reportlib.init(sys.argv[0], '', os.environ['QCOUTPUTDIR'])

fp.write('Marker used in Annotation differs from Marker used in Protein Isoform Ontology\n\n')
fp.write('value\tannotation\tontology\n\n')

results = db.sql('''select p.value, m.symbol as annotation, pm.symbol as isoformlookup
        from VOC_Annot a, VOC_Evidence e, VOC_Evidence_Property p, VOC_Term t, MRK_Marker m,
                ACC_Accession pa1, VOC_Annot pa, MRK_Marker pm
        where a._AnnotType_key = 1000
        and a._Object_key = m._Marker_key
        and a._Annot_key = e._Annot_key
        and e._AnnotEvidence_key = p._AnnotEvidence_key
        and p._PropertyTerm_key = t._Term_key
        and t.term = 'gene product'
        and p.value like 'PR:%'
        and p.value = pa1.accID
        and pa1._MGIType_key = 13
        and pa1._Object_key = pa._Term_key
        and pa._AnnotType_key = 1019
        and pa._Object_key = pm._Marker_key
        and m.symbol != pm.symbol
	''', 'auto')

for r in results:
    fp.write(r['value'] + TAB)
    fp.write(r['annotation'] + TAB)
    fp.write(r['isoformlookup'] + CRT)

#
# GPI
#
fp.write('\n\n(gene product) values that do not exist in GPI\n\n')
fp.write('value\tannotated marker\n\n')

#
# read/store object-to-Marker info
#
for line in gpiFile.readlines():
    if line[:1] == '!':
        continue
    tokens = line[:-1].split('\t')
    if tokens[0] in gpiSet:
        key = tokens[0] + ':' + tokens[1]
	gpiLookup.append(key)

results = db.sql('''select distinct p.value, m.symbol
        from VOC_Annot a, VOC_Evidence e, VOC_Evidence_Property p, MRK_Marker m
        where a._AnnotType_key = 1000
        and a._Object_key = m._Marker_key
        and a._Annot_key = e._Annot_key
        and e._AnnotEvidence_key = p._AnnotEvidence_key
        and p._PropertyTerm_key = 6481775
	order by p.value, m.symbol
	''', 'auto')

for r in results:
    if r['value'] not in gpiLookup:
    	fp.write(r['value'] + TAB)
    	fp.write(r['symbol'] + CRT)

reportlib.finish_nonps(fp)

