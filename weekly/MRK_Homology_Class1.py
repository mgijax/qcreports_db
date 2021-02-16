
'''
#
# MRK_Homology_Class1.py
#
# Report:
#
#       Classes for which there are > n genes from a single species
#
# Usage:
#       MRK_Homology_Class1.py
#
# Notes:
#
# History:
#
# sc    02/11/2021
#       TR13349 - B39 project. Update to use alliance direct homology
#               (was using Homologene)
#
# sc   01/24/2013
#       - TR6519/N2MO project
#
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

# Organism keys
MOUSE_KEY = 1
HUMAN_KEY = 2
RAT_KEY = 40
ZFISH_KEY = 84

# we want to report homolog clusters where any individual organism has
# greater than this number of members in a cluster
#
MAX = 10
fp = reportlib.init(sys.argv[0], 'Homology classes for which there are > 10 genes from a single species ', outputdir = os.environ['QCOUTPUTDIR'])

fp.write('HomoloGeneID%sHuman gene count%sMouse gene count%sRat gene count%sZebrafish gene count%s' % (TAB, TAB, TAB, TAB, CRT))

#
# get all clusters and their members for cluster source 'HomoloGene' and
# cluster type 'homology'
#
results = db.sql('''select mc._cluster_key, mcm._Marker_key, m._Organism_key
            from MRK_Cluster mc, MRK_ClusterMember mcm, MRK_Marker m
            where mc._ClusterType_key = 9272150
            and mc._ClusterSource_key = 75885739
            and mc._Cluster_key = mcm._Cluster_key
            and mcm._Marker_key = m._Marker_key
            order by mc._Cluster_key''', 'auto')

clusterDict = {}
for r in results:
    clusterKey = int(r['_cluster_key'])
    orgKey = r['_Organism_key']
    if clusterKey not in clusterDict:
        clusterDict[clusterKey] = {'mouse':0, 'human':0, 'rat':0, 'zebrafish':0}
    if orgKey == MOUSE_KEY:
        clusterDict[clusterKey]['mouse'] += 1
    elif orgKey == HUMAN_KEY:
        clusterDict[clusterKey]['human'] += 1
    elif orgKey == RAT_KEY:
        clusterDict[clusterKey]['rat'] += 1
    elif orgKey == ZFISH_KEY:
        clusterDict[clusterKey]['zebrafish'] += 1

cKeyList = sorted(clusterDict.keys() )
for key in cKeyList:
    reportHomology = 0
    if clusterDict[key]['mouse'] > MAX:
        reportHomology = 1
    elif clusterDict[key]['human'] > MAX:
        reportHomology = 1
    elif clusterDict[key]['rat'] > MAX:
        reportHomology = 1
    elif clusterDict[key]['zebrafish'] > MAX:
        reportHomology = 1

    if reportHomology == 1:
        fp.write('%s%s%s%s%s%s%s%s%s%s' % (key, TAB, clusterDict[key]['human'], TAB, clusterDict[key]['mouse'], TAB, clusterDict[key]['rat'],  TAB, clusterDict[key]['zebrafish'], CRT) )

reportlib.finish_nonps(fp)
