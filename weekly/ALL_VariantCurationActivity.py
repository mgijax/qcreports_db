#
# Report:
#       Variant Curation Activity
#
# curator (one column for any curator associated with variant curation)
# number of unique allele/variants records created for each curator that week
#
# Report should be yearly (52 rows).
# One number per cell (created).
#
# History:
#
# lec	05/22/2023
#	- wts2-1185/fl2-355/Variant Curation Activity Report
#
 
import sys 
import os
import db
import reportlib

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

variantUser = []
variantByUser = {}
variantByWeek = {}

fp = reportlib.init(sys.argv[0], 'Variant Curation Activity Report', os.environ['QCOUTPUTDIR'])

results = db.sql('''
select distinct u.login
from ALL_Variant v, MGI_User u
where v._createdby_key = u._user_key
and date_part('year', v.creation_date) = date_part('year', CURRENT_DATE)
order by u.login
''', 'auto')
for r in results:
	variantUser.append(r['login'])

results = db.sql('''
select count(distinct v._allele_key) as countByWeek, u.login, 
	date_trunc('week', v.creation_date + interval '-1 day') - interval '1 days' as weekly
from ALL_Variant v, MGI_User u
where v._createdby_key = u._user_key
and v._sourcevariant_key is not null
and date_part('year', v.creation_date) = date_part('year', CURRENT_DATE)
group by u.login, weekly
order by weekly, u.login
''', 'auto')

for r in results:
	u = r['login']
	w = r['weekly']
	if w not in variantByWeek:
		variantByWeek[w] = []
	variantByWeek[w].append(r)
	if u not in variantByUser:
		variantByUser[u] = []
	variantByUser[u].append(r)

# set of variant users
fp.write(TAB*2)
for u in variantUser:
	fp.write(u + TAB)
fp.write(CRT)

# count of distinct variant alleles by week & user
for v in variantByWeek:
	fp.write(v[:10] + TAB)
	for u in variantUser:
		foundUser = 0
		for vv in variantByWeek[v]:
			if u == vv['login']:
				foundUser = 1
				break
		if foundUser == 1:
			fp.write(str(vv['countByWeek']) + TAB)
		else:
			fp.write('0' + TAB)

	fp.write(CRT)

reportlib.finish_nonps(fp)	# non-postscript file

