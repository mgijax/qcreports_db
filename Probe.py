#!/usr/local/bin/python

'''
#
# Probe.py 11/16/98
#
# Report:
#       Detail information for Molecular Segments
#
# Usage:
#       Probe.py
#
# Generated from:
#       Editing Interface Molecular Segments Reports
#
# Notes:
#
# History:
#
# lec	01/13/98
#	- added comments section
#
'''
 
import sys 
import os
import string
import regsub
import mgdlib
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

columns = reportlib.column_width

row = 1
present_rflv_key = 0
present_allele_key = 0

probe_info = ''
alias_string = ''
header = ''

def write(string):
	global probe_info

	probe_info = probe_info + string 

def crt(count):
	global row

	row = row + count
	return(count * CRT)

def parse_alias(alias):
	global alias_string 

	if len(alias_string) > 0:
		alias_string = alias_string + ','
	alias_string = alias_string + mgdlib.prvalue(alias['alias'])
	write(reportlib.format_line(mgdlib.prvalue(alias['alias'])))

def parse_marker(marker):
	write(TAB + string.ljust(mgdlib.prvalue(marker['symbol']), 20))
	write(string.ljust(mgdlib.prvalue(marker['chromosome']), 20))
	write(string.ljust(mgdlib.prvalue(marker['relationship']), 20) + crt(1))

def parse_clone(probe):
	write(TAB + string.ljust('Parent Clone:  ', 15) + \
	      mgdlib.prvalue(probe['parentClone']) + \
	      ' (' + probe['parentID'] + ')' + crt(1))

def parse_source(probe):
       	write(TAB + string.ljust('Species:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['species']), 20))
	write(string.rjust('Strain:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['strain']), 20) + crt(1))
       	write(TAB + string.ljust('Tissue:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['tissue']), 20))
       	write(string.rjust('Cell Line:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['cellLine']), 20) + crt(1))
       	write(string.rjust('Tissue Treatment:  ', 20) + \
		string.ljust(mgdlib.prvalue(probe['description']), 30) + crt(1))
       	write(TAB + string.ljust('Age:', 15) + \
		string.ljust(mgdlib.prvalue(probe['age']), 20))
       	write(string.rjust('Sex:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['sex']), 20) + crt(1))

def parse_note(note):
	write(reportlib.format_line(mgdlib.prvalue(note['note'])))

def parse_ref_notes(note):
	write(reportlib.format_line(mgdlib.prvalue(note['note'])))

def parse_rflv(rflv):
	if (rflv['_RFLV_key'] != None):
		cmd = 'select rf.endonuclease, a.* , als.* , s.* , l.symbol ' + \
		      'from PRB_RFLV rf, PRB_Allele a, PRB_Strain s, ' + \
		      'PRB_Allele_Strain als, MRK_Mouse_View l ' + \
		      'where rf._RFLV_key = %d' % rflv['_RFLV_key'] + \
		      ' and rf._Marker_key = l._Marker_key' + \
		      ' and rf._RFLV_key = a._RFLV_key' + \
		      ' and a._Allele_key = als._Allele_key' + \
		      ' and als._Strain_key = s._Strain_key'
		mgdlib.sql(cmd, parse_alleles)

def parse_alleles(alleles):
	global present_rflv_key
	global present_allele_key

	if (present_rflv_key != alleles['_RFLV_key']):
                write(string.ljust(mgdlib.prvalue(alleles['endonuclease']), 15))
		write(string.ljust(mgdlib.prvalue(alleles['symbol']), 15))
           	present_rflv_key = alleles['_RFLV_key']
        else:
                write(string.ljust(' ', 30))

	if (present_allele_key != alleles['_Allele_key']):	
        	write(string.ljust(mgdlib.prvalue(alleles['allele']), 10))
		write(string.ljust(mgdlib.prvalue(alleles['fragments']), 30))
		present_allele_key = alleles['_Allele_key']
	else:
                write(string.ljust(' ', 40))

 	write(mgdlib.prvalue(alleles['strain']) + crt(1))

def parse_acc(acc):
	write(acc['LogicalDB'] + ' Acc#:  ' + acc['accID'] + crt(1))

def parse_probe_key(probe_key):
	global fp
	global header
	global probe_info
	global alias_string
	global row

	if (row > 1):
		if (alias_string == ''):
			header = header + (crt(1))
		else:
			header = header + alias_string + crt(1)

		write(PAGE)
		row = 1

	if fp is None:	
		reportName = regsub.gsub(' ', '-', probe_key['name'])
		reportName = regsub.gsub('/', '', reportName)
		reportName = 'Probe.' + reportName + '.rpt'
		fp = reportlib.init(reportName, 'Molecular Probes and Segments', os.environ['QCREPORTOUTPUTDIR'])

	fp.write(header + probe_info)
	header = ''
	probe_info = ''
	alias_string = ''

	cmd = 'select * from PRB_View where _Probe_key = %d' % probe_key['_Probe_key']
	mgdlib.sql(cmd, parse_probe)

def parse_probe(probe):
	global header
	global probeName

	date = probe['modification_date']

	probeName = probe['name']
	header = header + string.ljust('Name:  ', 10) + mgdlib.prvalue(probe['name']) + 4*TAB
	header = header + 'Modified:  ' + `date[1]` + '/' + `date[2]` + '/' + `date[0]` + crt(1)
	header = header + string.ljust('Aliases:  ', 10)

	write(crt(1))
	cmd = 'select accID, LogicalDB from PRB_AccNoRef_View ' + \
	      'where _Object_key = %d' % probe['_Probe_key'] + \
	      ' order by _LogicalDB_key'
	mgdlib.sql(cmd, parse_acc)
	write(crt(1))

	write(string.rjust('Sequence Type:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['DNAtype']), 20) + crt(1))
	write(reportlib.format_line('Region Covered:  ' + \
        mgdlib.prvalue(probe['regionCovered']) + \
		mgdlib.prvalue(probe['regionCovered2'])) + crt(2))
	write(TAB + string.ljust('Marker', 20) + \
		string.ljust('Chromosome', 20) + \
		string.ljust('Relationship', 20) + crt(2))

	cmd = 'select symbol, chromosome, relationship from PRB_Marker_View ' + \
	      'where _Probe_key = %d' % probe['_Probe_key']
	mgdlib.sql(cmd, parse_marker)
	write(crt(2))

	if probe['DNAtype'] == 'primer':
        	write('Product size:  ' + \
			mgdlib.prvalue(probe['productSize']) + crt(1))
        	write('Sequence 1  :  ' + \
			mgdlib.prvalue(probe['primer1sequence']) + crt(1))
        	write('Sequence 2  :  ' + \
			mgdlib.prvalue(probe['primer2sequence']) + crt(1))
        	write('Repeat unit :  ' + \
			reportlib.format_line(mgdlib.prvalue(probe['repeatUnit'])) + crt(1))
	else:
		if probe['derivedFrom'] is not None:
			cmd = 'select distinct parentClone, parentID ' + \
			      'from PRB_Parent_View ' + \
			      'where parentKey = %d' % probe['derivedFrom']
			mgdlib.sql(cmd, parse_clone)

		cmd = 'select * from PRB_Source_View ' + \
		      'where _Source_key = %d' % probe['_Source_key']
		mgdlib.sql(cmd, parse_source)

       		write(TAB + string.ljust('Vector Type:  ', 15) + \
			string.ljust(mgdlib.prvalue(probe['vectorType']), 20))
       		write(string.rjust('Insert site:  ', 15) + \
			string.ljust(mgdlib.prvalue(probe['insertSite']), 20))
		write(crt(1) + TAB)

       	write(string.ljust('Insert size:  ', 15) + \
		string.ljust(mgdlib.prvalue(probe['insertSize']), 20) + crt(2))

	write('Comments:  ' + crt(1))
	cmd = 'select note from PRB_Notes where _Probe_key = %d' % probe['_Probe_key']
	mgdlib.sql(cmd, parse_note)
	write(crt(1) + 80 * '_' + crt(2))

	cmd = 'select * from PRB_Reference_View where _Probe_key = %d' % probe['_Probe_key']
	mgdlib.sql(cmd, parse_ref)

def parse_ref(ref):
	global probeName

	write(string.ljust('Name:  ', 10) + mgdlib.prvalue(probeName) + crt(1))
	write(string.ljust('Ref:  ', 10) + 'J' + mgdlib.prvalue(ref['jnum']) + \
	      SPACE + mgdlib.prvalue(ref['short_citation']) + crt(1))
	write(string.ljust('Holder:  ', 10) + mgdlib.prvalue(ref['holder']) + crt(1))
	write(string.ljust('Aliases:  ', 10) + crt(2))

	cmd = 'select accID, LogicalDB from PRB_AccRef_View ' + \
	      'where _Reference_key = ' + `ref['_Reference_key']` + \
	      ' order by _LogicalDB_key'
	mgdlib.sql(cmd, parse_acc)

	cmd = 'select alias from PRB_Alias where _Reference_key = ' + `ref['_Reference_key']`
	mgdlib.sql(cmd, parse_alias)

	cmd = 'select note from PRB_Ref_Notes where _Reference_key = ' + `ref['_Reference_key']`
	write(crt(2) + string.ljust('Notes:  ', 10))
	mgdlib.sql(cmd, parse_ref_notes)

	write(crt(2) + string.ljust('RFLVs:  ', 10) + crt(2))
	write(string.ljust('Endonuclease', 15))
	write(string.ljust('Marker', 15))
	write(string.ljust('Allele', 10))
	write(string.ljust('Fragments', 30))
	write('Strains' + crt(1))

	cmd = 'select * from PRB_RFLV where _Reference_key = ' + `ref['_Reference_key']`
	mgdlib.sql(cmd, parse_rflv)
	write(crt(1))

	if (ref['hasSequence'] == 1):
		write(TAB + '[X] Has sequence presented' + crt(1))
	else:
		write(TAB + '[ ] Has sequence presented' + crt(1))
 
	if (ref['hasRmap'] == 1):
		write(TAB + '[X] Has RMap information' + crt(1))
	else:
		write(TAB + '[ ] Has RMap information' + crt(1))

	write(80 * '_' + crt(2))

#
# Main
#

fp = None
cmd = sys.argv[1]
mgdlib.sql(cmd, parse_probe_key)
header = header + alias_string + crt(1)

if fp is not None:
	fp.write(header + probe_info)
	reportlib.finish_nonps(fp)

