#!/usr/local/bin/python

'''
#
# Strain.py 11/16/98
#
# Report:
#	Basic Strain Info
#
# Usage:
#       Strain.py
#
# Generated from:
#       Editing Interface Strains Form
#
# Notes:
#
# History:
#
# lec	06/09/98
#	- added Expression results
#	- added message indicating if Molecular Segments are included
#
# lec	02/10/98
#	- modifications per Moyha
#
# lec	02/09/98
#	- created
#
'''
 
import sys
import os
import string
import regsub
import mgdlib
import reportlib

CRT = reportlib.CRT
SP = reportlib.SPACE
fp = None

strains = mgdlib.sql(sys.argv[1], 'auto')

try:
	retrieveProbes = sys.argv[2]
except:
	retrieveProbes = 0

for s in strains:

	cmds = []

	cmds.append('select distinct e._Refs_key, _Probe_key = NULL, dataSet = "Mapping" ' + \
                  'into #references ' + \
                  'from MLD_Expts e, MLD_InSitu m ' + \
                  'where e._Expt_key = m._Expt_key ' + \
                  'and m._Strain_key = %s' % s['_Strain_key'] + \
                  ' union ' + \
                  'select distinct e._Refs_key, _Probe_key = NULL, dataSet = "Mapping" ' + \
                  'from MLD_Expts e, MLD_FISH m ' + \
                  'where e._Expt_key = m._Expt_key ' + \
                  'and m._Strain_key = %s' % s['_Strain_key'] + \
                  ' union ' + \
                  'select distinct e._Refs_key, _Probe_key = NULL, dataSet = "Mapping" ' + \
                  'from MLD_Expts e, MLD_Matrix m, CRS_Cross c ' + \
                  'where e._Expt_key = m._Expt_key ' + \
                  'and m._Cross_key = c._Cross_key ' + \
                  'and c._femaleStrain_key = %s' % s['_Strain_key'] + \
                  ' union ' + \
                  'select distinct e._Refs_key, _Probe_key = NULL, dataSet = "Mapping" ' + \
                  'from MLD_Expts e, MLD_Matrix m, CRS_Cross c ' + \
                  'where e._Expt_key = m._Expt_key ' + \
                  'and m._Cross_key = c._Cross_key ' + \
                  'and c._maleStrain_key = %s' % s['_Strain_key'] + \
                  ' union ' + \
                  'select distinct e._Refs_key, _Probe_key = NULL, dataSet = "Mapping" ' + \
                  'from MLD_Expts e, MLD_Matrix m, CRS_Cross c ' + \
                  'where e._Expt_key = m._Expt_key ' + \
                  'and m._Cross_key = c._Cross_key ' + \
                  'and c._StrainHO_key = %s' % s['_Strain_key'] + \
                  ' union ' + \
                  'select distinct e._Refs_key, _Probe_key = NULL, dataSet = "Mapping" ' + \
                  'from MLD_Expts e, MLD_Matrix m, CRS_Cross c ' + \
                  'where e._Expt_key = m._Expt_key ' + \
                  'and m._Cross_key = c._Cross_key ' + \
                  'and c._StrainHT_key = %s' % s['_Strain_key'] + \
                  ' union ' + \
                  'select distinct a._Refs_key, _Probe_key = NULL, dataSet = "Expression" ' + \
                  'from GXD_Genotype s, GXD_Expression x, GXD_Assay a ' + \
                  'where s._Strain_key = %s' % s['_Strain_key'] + \
                  'and s._Genotype_key = x._Genotype_key ' + \
                  'and x._Assay_key = a._Assay_key ' + \
                  ' union ' + \
                  'select distinct r._Refs_key, r._Probe_key, dataSet = "RFLP" ' + \
                  'from PRB_Reference r, PRB_RFLV v, PRB_Allele a, PRB_Allele_Strain s ' + \
                  'where r._Reference_key = v._Reference_key ' + \
                  'and v._RFLV_key = a._RFLV_key ' + \
                  'and a._Allele_key = s._Allele_key ' + \
                  'and s._Strain_key = %s' % s['_Strain_key'])

	lastCmd = 'select a.accID, a.prefixPart, a.numericPart, r.dataSet, r._Probe_key ' + \
                  'from #references r, BIB_Acc_View a ' + \
                  'where r._Refs_key = a._Object_key ' + \
                  'and r.dataSet != "Molecular Segment" ' + \
                  'and a.prefixPart = "J:" ' + \
		  'union ' + \
	          'select a.accID, a.prefixPart, a.numericPart, r.dataSet, r._Probe_key ' + \
                  'from #references r, PRB_Acc_View a ' + \
                  'where r._Probe_key = a._Object_key ' + \
                  'and r.dataSet != "Molecular Segment" ' + \
                  'and a.prefixPart = "MGI:"\n'

	if retrieveProbes:
		# Retrieve all Probes for all Source records for specified Strain

		cmds.append('select p._Probe_key, dataSet = "Molecular Segment"' + \
                   	'into #probes ' + \
                   	'from PRB_Source s, PRB_Probe p ' + \
                   	'where s._Strain_key = %s' % s['_Strain_key'] + \
                   	'and s._Source_key = p._Source_key\n')
 
		# Union together the References and Probes for specified Strain

		lastCmd = lastCmd + \
		   '\nunion ' + \
	            'select a.accID, a.prefixPart, a.numericPart, p.dataSet, p._Probe_key ' + \
                   'from #probes p, PRB_Acc_View a ' + \
                   'where p._Probe_key = a._Object_key ' + \
                   'and a.prefixPart = "MGI:" ' + \
                   'and a.preferred = 1\n'

	lastCmd = lastCmd + 'order by _Probe_key'
	cmds.append(lastCmd)

	references = mgdlib.sql(cmds, 'auto')
	prevStrain = ''
	prevProbe = ''

	for r in references[len(references) - 1]:

		if fp is None:  
			reportName = regsub.gsub(' ', '', s['strain'])
			reportName = regsub.gsub('/', '', reportName)
			reportName = 'Strain.%s.rpt' % reportName
			fp = reportlib.init(reportName, 'Strains', os.environ['QCREPORTOUTPUTDIR'])

			if retrieveProbes:
				fp.write(CRT)
				fp.write('Molecular Segments Included')
			else:
				fp.write(CRT)
				fp.write('Molecular Segments NOT Included')

		if prevStrain != s['strain']:
			fp.write(2 * CRT)
			fp.write('Strain: %s' % s['strain'])
			fp.write(2*CRT)
			fp.write(string.ljust('DataSet', 20))
			fp.write('Accession #')
			fp.write(CRT)
			fp.write(string.ljust('-------', 20))
			fp.write('-----------')
			fp.write(CRT)
			prevStrain = s['strain']

		# For same RFLP Probe, print all Accession numbers on one line

		if r['dataSet'] == 'RFLP':
			if prevProbe != r['_Probe_key']:
				fp.write(CRT + string.ljust(r['dataSet'], 20))
				fp.write(r['accID'])
				prevProbe = r['_Probe_key']
			else:
				fp.write(',' + r['accID'])
		else:
			fp.write(CRT + string.ljust(r['dataSet'], 20))
			fp.write(r['accID'])

reportlib.finish_nonps(fp)

