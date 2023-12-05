
'''
#
# MRK_Homology_NoHuman.py
#
# Report:
#
#       Mouse genes with no human homolog
#
# Usage:
#       MRK_Homology_NoHuman.py
#
# Notes:
#
# History:
#
# sc   11/28/2023
#       - WTS2-356/TR12204
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

noHumanCount = 0

fp = reportlib.init(sys.argv[0], 'Mouse Genes that have no Human Homolog', outputdir = os.environ['QCOUTPUTDIR'])
fp.write(CRT)
fp.write('## Mouse Genes Only%s' % CRT)
fp.write('## Exclude feature types: %s' % CRT)
fp.write('##   "heritable phenotypic marker"%s' % CRT)
fp.write('##   "gene segment"%s' % CRT)
fp.write(CRT)
fp.write('Mouse ID%sMouse Symbol%s' % (TAB, CRT))

# get all clusters that have human homology and create a lookup
humanList = []
results = db.sql('''select distinct mc._cluster_key
            from MRK_Cluster mc, MRK_ClusterMember mcm, MRK_Marker m
            where mc._ClusterType_key = 9272150
            and mc._ClusterSource_key = 75885739
            and mc._Cluster_key = mcm._Cluster_key
            and mcm._Marker_key = m._Marker_key
            and m._organism_key = 2
            order by mc._Cluster_key''', 'auto')
for r in results:
    humanList.append(r['_cluster_key'])

#
# get all clusters with mouse members for cluster source 'Alliance Direct' and
# cluster type 'homology'
#
db.sql('''select mc._cluster_key, m.markertype, m.symbol, a.accid, 
            mcm._marker_key, m._organism_key
        into temporary table mouseHomology
        from mrk_cluster mc, mrk_clustermember mcm, 
            mrk_marker_view m, acc_accession a
        where m._organism_key = 1 -- if it has an MGI ID has to be a mouse, but make this obvious
        and mc._clustertype_key = 9272150
        and mc._clustersource_key = 75885739
        and mc._cluster_key = mcm._Cluster_key
        and mcm._marker_key = m._marker_key
        and m.markertype = 'Gene'
        and m._marker_key = a._object_key
        and a._mgitype_key = 2
        and a._logicaldb_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1''', None)

db.sql('''create index idx1 on mouseHomology(_marker_key)''', None)

# exclude feature types hpm and gm
results = db.sql('''select mh.*, mcv.term
    from mouseHomology mh, mrk_mcv_cache mcv
    where mh._marker_key = mcv._marker_key
    and mcv.qualifier = 'D'
    and mcv.term != 'heritable phenotypic marker'
    and mcv.term != 'gene segment' 
    order by mh.symbol''', 'auto')

for r in results:
    clusterKey = r['_cluster_key']
    if clusterKey not in humanList:
        noHumanCount += 1
        fp.write('%s%s%s%s' % (r['accid'], TAB, r['symbol'], CRT) )

fp.write('%sTotal: %s' % (CRT, noHumanCount))
reportlib.finish_nonps(fp)
