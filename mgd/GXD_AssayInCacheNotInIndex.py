
'''
#
# TR 8820
#
# Report:
#
# Please see the body of TR8820 for details, the description is too long to list here.
# In a nutshell however, this is looking for all assays that exist in the GXD cache, 
# that DO NOT exist in the 
# GXD index.
#
# Usage:
#       GXD_AssayInCacheNotInIndex.py
#
# Notes:
#
# History:
#
# mhall	05/12/2009
#	- TR 8820- created
#
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('Full coded assays that were not indexed' + CRT)

# Gather up all of the assay's that are in the index

db.sql('''
        select distinct ga._Assay_key, gis._IndexAssay_key 
        into temporary table indexAssays
        from GXD_Assay ga, GXD_Index gi, GXD_Index_Stages gis
        where gi._Index_key = gis._Index_key 
        and gi._Refs_key = ga._Refs_key and gi._Marker_key = ga._Marker_key
        ''', None)

db.sql('create index iaIndex on indexAssays (_Assay_key, _IndexAssay_key)', None)

# Grab the display information for the items in GXD_Expression

db.sql('''
        select distinct bcc.jnumID as jnum, a.accID as mgiid, 
               ge._Assay_key, ge._AssayType_key, gat.assayType, u.login
        into temporary table cacheAssayLookup
        from GXD_Expression ge, ACC_Accession a, BIB_Citation_Cache bcc, GXD_AssayType gat, 
                GXD_Assay ga, MGI_User u
        where ge._Assay_key = a._Object_key 
        and a.prefixPart = 'MGI:'
        and a._MGIType_key = 8 
        and ge._Refs_key = bcc._Refs_key
        and ge._AssayType_key in (1, 2, 3, 4, 5, 6, 8, 9)
        and ge._AssayType_key = gat._AssayType_key
        and ge._Assay_key = ga._Assay_key
        and ga._ModifiedBy_key = u._User_key
        ''', None)

db.sql('create index caLookupindex on cacheAssayLookup (_Assay_key, _AssayType_key)', None)

# Check the various assay type relationships, bringing back those that are missing
# for each type

results = db.sql('''
        (
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 1 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74718, 74720))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 2 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74722))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 3 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74727))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 4 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74726))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 5 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74724))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 6 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74717, 74719))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 8 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74723))
        union
        select distinct cal.jnum, cal.mgiid, cal.assayType, cal.login
        from GXD_Expression ge, cacheAssayLookup cal
        where ge._AssayType_key = 9 and ge._Assay_key = cal._Assay_key
        and not exists (select 1 from indexAssays iak 
        where ge._Assay_key = iak._Assay_key 
        and iak._IndexAssay_key in (74721))
        )
        order by jnum
        ''', 'auto')

for item in results:
        fp.write(item['jnum'] + TAB + item['mgiid'] + TAB + item['assayType'] + TAB + item['login'] + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
