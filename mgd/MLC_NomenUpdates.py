#!/usr/local/bin/python

'''
#
# Recent Nomenclature Events Report for MLC only
#
# Report:
#       template for creating Python reports
#
# Usage:
#       MLC_NomenUpdates.py
#
# Notes:
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	01/04/99
#	- created
#
'''
 
import sys 
import os
import db
import mgi_utils
import reportlib

#
# Main
#

currentReport = 'MLCNomenclature-current.html'

# remove current report link if it exists
if os.path.isfile('%s/%s' % (os.environ['EIREPORTDIR'], currentReport)):
	os.remove('%s/%s' % (os.environ['EIREPORTDIR'], currentReport))

# move existing Nomen reports to the archive
os.system('mv %s/MLCNomenclature-*.html %s/archive/nomen' % (os.environ['EIREPORTDIR'], os.environ['EIREPORTDIR']))

reportName = 'MLCNomenclature-' + mgi_utils.date('%Y-%m-%d')

currentDate = mgi_utils.date('%m/%d/%Y')

results = db.sql('select convert(varchar(25), dateadd(day, -7, "%s"))' % (currentDate), 'auto')
bdate = results[0]['']

results = db.sql('select convert(varchar(25), dateadd(day, 0, "%s"))' % (currentDate), 'auto')
edate = results[0]['']

title = 'Updates to MLC Mouse Nomenclature from %s to %s' % (bdate, edate)
fp = reportlib.init(reportName, title, os.environ['EIREPORTDIR'], isHTML = 1)

fp.write('J:23000 generally indicates gene family nomenclature revision event.\n\n')

cmd = []

cmd.append('select m._Marker_key, m.mgiID, c.sequenceNum, h._Refs_key ' + \
'into #m1 ' + \
'from MRK_Mouse_View m, MRK_History h, MRK_Chromosome c, MLC_Text_edit mlc ' + \
'where m.creation_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and "%s" ' % (currentDate) + \
'and m._Marker_key = h._Marker_key ' + \
'and m._Marker_key = h._History_key ' + \
'and h._Marker_Event_key = 1 ' + \
'and m.chromosome = c.chromosome ' + \
'and m._Species_key = c._Species_key ' + \
'and m._Marker_key = mlc._Marker_key ' + \
'union ' + \
'select h._History_key, m.mgiID, sequenceNum = 100, h._Refs_key ' + \
'from MRK_History h, MRK_Mouse_View m, MLC_Text_edit mlc ' + \
'where h.event_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and "%s" ' % (currentDate) + \
'and h._Marker_key = m._Marker_key ' + \
'and h._Marker_Event_key in (2,3,4,5) ' + \
'and m._Marker_key = mlc._Marker_key'
)

cmd.append('select ' + \
'chr = substring(r.chromosome,1,2), ' + \
'm.mgiID, r.symbol,  ' + \
'name = substring(r.name,1,25),  ' + \
'b.jnumID, jnum = convert(char(6), b.jnum), ' + \
'author = substring(b._primary, 1, 16) ' + \
'from #m1 m, MRK_Marker r, BIB_All_View b ' + \
'where m._Marker_key = r._Marker_key ' + \
'and m._Refs_key = b._Refs_key ' + \
'order by m.sequenceNum, r.symbol'
)

results = db.sql(cmd, 'auto')

fp.write('%-2s %-25s %-25s %-6s %-16s\n' % ('Ch', 'Symbol', 'Gene Name', 'J#', 'First Author'))
fp.write('%-2s %-25s %-25s %-6s %-16s\n' % ('--', '------', '---------', '--', '------------'))

rows = 0
for r in results[1]:
	fp.write('%-2s ' % (r['chr']))

	if r['mgiID'] != "None":
		fp.write('<A HREF="http://prodwww.informatics.jax.org/searches/accession_report.cgi?id=%s">%-25s</A> ' % (r['mgiID'], r['symbol']))
	else:
		fp.write('%-25s ' % (r['symbol']))
		
	fp.write('%-25s ' % (r['name']))
	fp.write('<A HREF="http://prodwww.informatics.jax.org/searches/accession_report.cgi?id=%s">%-6s</A> ' % (r['jnumID'], r['jnum']))
	fp.write('%-16s\n' % (r['author']))
	rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp, isHTML = 1)	# non-postscript file

# re-create a symbolic link between the new file and the current file

os.chdir(os.environ['EIREPORTDIR'])
os.symlink(reportName + '.html', currentReport)

