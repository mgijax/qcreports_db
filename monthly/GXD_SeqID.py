#!/usr/local/bin/python

'''
#
# TR 7859/TR 7859
#
# Report:
#       Produce a report of probes with ALL of the following conditions:
#
#       1) The probe is used in a GXD assay
#       2) The probe has a seq ID attached to it
#       3) The probe has an encodes relationship to a marker
#       4) The seq ID associated with the probe is also associated with
#          another marker other than the one that it has an encodes
#          relationship with
#
#       The report should have the following columns:
#
#       1) MGI ID of the probe
#       2) Name of the probe
#       3) Seq ID
#
# Usage:
#       GXD_SeqID.py
#
# Notes:
#
# History:
#
# lec	08/25/2006
#	- converted to QC report
#
# dbm    8/16/2006    created
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


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE


#
# Main
#

#
# Open the output file and write a header to it.
#
fp = reportlib.init(sys.argv[0], 'Probes used in GXD Assay w/ Seq IDs/Seq ID Attached to another Marker', os.environ['QCOUTPUTDIR'])
fp.write('Probe MGI ID    Probe Name                        Seq ID' + CRT)
fp.write('------------    ------------------------------    ------------' + CRT)

#
# Find all probes that are used in a GXD assay and also have an encodes
# relationship with a marker.
#
db.sql(
    'select a.accID "mgiID", ' + \
           'p._Probe_key, ' + \
           'p.name "probeName", ' + \
           'pm._Marker_key ' + \
    'into #prbmrk ' + \
    'from PRB_Probe p, ' + \
         'PRB_Marker pm, ' + \
         'ACC_Accession a ' + \
    'where exists (select 1 ' + \
                  'from GXD_ProbePrep gp ' + \
                  'where gp._Probe_key = p._Probe_key) and ' + \
          'p._Probe_key = pm._Probe_key and ' + \
          'pm.relationship = "E" and ' + \
          'p._Probe_key = a._Object_key and ' + \
          'a._MGIType_key = 3 and ' + \
          'a._LogicalDB_key = 1 and ' + \
          'a.prefixPart = "MGI:" and ' + \
          'a.preferred = 1', None)

#
# From the previous list of probes/markers, find the ones that have a
# seq ID association.
#
db.sql(
    'select pm.*, a1.accID "seqID", ' + \
           'a2._Object_key "_Sequence_key" ' + \
    'into #prbseq ' + \
    'from ACC_Accession a1, ' + \
         'ACC_Accession a2, ' + \
         '#prbmrk pm ' + \
    'where pm._Probe_key = a1._Object_key and ' + \
          'a1._MGIType_key = 3 and ' + \
          'a1._LogicalDB_key = 9 and ' + \
          'a2.accID = a1.accID and ' + \
          'a2._MGIType_key = 19 and ' + \
          'a2._LogicalDB_key = 9 and ' + \
          'a2.preferred = 1', None)

#
# From the previous list of probes/marker/sequences, find the ones where
# the seq ID is also associated with a different marker.
#
results = db.sql(
    'select distinct ps.mgiID, ps.probeName, ps.seqID ' + \
    'from #prbseq ps, ' + \
         'SEQ_Marker_Cache sm ' + \
    'where ps._Sequence_key = sm._Sequence_key and ' + \
          'ps._Marker_key != sm._Marker_key', 'auto')

#
# Process each row of the results set.
#
for r in results:

    #
    # Write a row of data to the output file.
    #
    fp.write("%-12s    %-30s    %-12s\n" % (r['mgiID'],r['probeName'],r['seqID']))

#
#
reportlib.finish_nonps(fp)
