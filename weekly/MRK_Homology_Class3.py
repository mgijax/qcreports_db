#!/usr/local/bin/python

'''
#
# MRK_Homology_Class3.py
#
# Report:
#
#       Classes for which there are >n genes from a single species
#
# Usage:
#       MRK_Homology_Class3.py
#
# Notes:
#
# History:
#
# sc   01/24/2013
#       - TR6519/N2MO project
#
#
'''

import sys
import os
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

TAB = reportlib.TAB
CRT = reportlib.CRT

# Organism keys
MOUSE_KEY = 1
HUMAN_KEY = 2
RAT_KEY = 40
CATTLE_KEY = 11
CHIMP_KEY = 10
DOG_KEY = 13

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], 'Homology classes with only mouse genes ', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('HomoloGeneID%sMouse gene count%s' % (TAB, CRT))

#
# get all clusters and their members for cluster source 'HomoloGene' and
# cluster type 'homology'
#
results = db.sql('''select mc.clusterID, mcm._Marker_key, m._Organism_key
	    from MRK_Cluster mc, MRK_ClusterMember mcm, MRK_Marker m
	    where mc._ClusterType_key = 9272150
	    and mc._ClusterSource_key = 9272151
	    and mc._Cluster_key = mcm._Cluster_key
	    and mcm._Marker_key = m._Marker_key
	    order by mc._Cluster_key''', 'auto')

clusterDict = {}
for r in results:
    homologeneID = int(r['clusterID'])
    orgKey = r['_Organism_key']
    if not clusterDict.has_key(homologeneID):
	clusterDict[homologeneID] = {'mouse':0, 'human':0, 'rat':0, 'cattle':0, 'chimp':0, 'dog':0}
    if orgKey == MOUSE_KEY:
	clusterDict[homologeneID]['mouse'] += 1
    elif orgKey == HUMAN_KEY:
	clusterDict[homologeneID]['human'] += 1
    elif orgKey == RAT_KEY:
        clusterDict[homologeneID]['rat'] += 1
    elif orgKey == CATTLE_KEY:
        clusterDict[homologeneID]['cattle'] += 1
    elif orgKey == CHIMP_KEY:
        clusterDict[homologeneID]['chimp'] += 1
    elif orgKey == DOG_KEY:
        clusterDict[homologeneID]['dog'] += 1

idList = sorted(clusterDict.keys() )
for id in idList:
    if clusterDict[id]['mouse'] > 0:
	if clusterDict[id]['human'] == 0 and clusterDict[id]['rat'] == 0 and clusterDict[id]['cattle'] == 0 and clusterDict[id]['chimp'] == 0 and clusterDict[id]['dog'] == 0:
	    fp.write('%s%s%s%s' % (id, TAB, clusterDict[id]['mouse'], CRT) )  

reportlib.finish_nonps(fp)

