#!/usr/local/bin/python

'''
#
# GO_gp2protein.py (TR 6942, special MGI version, TR 4877, originally TR 3659)
#
# Report:
#       Tab-delimited file
#
# Usage:
#       GO_gp2protein.py
#
# Output
#
#	A tab-delimited file in this format:
#	field 1: MGI Marker ID
#	field 2: Swiss-Prot sequence ('SWP:' + seqID) OR
#	         TrEMBL sequence ('TR:' + seqID) OR
#	         RefSeq sequence ('NCBI:' + seqID) OR
#
# Used by:
#
#	Harold
#
# Notes:
#
# History:
#
# 12/24/2007	dbm
#	- TR 8697; complete re-write; Show all protein coding genes and
#	  their representative protein sequences, regardless of annotations.
#
# 08/01/2005	lec
#	- TR 6942; special version for Harold; include SP and TrEMBL
#
#	Created for TR3659.  
#	Report the MGI ID, SwissProt ID(s), and GO ID(s) for all mouse
#	markers that have associated SwissProt sequences.

'''
 
import sys
import string
import os
import db
import reportlib

#
# Main
#

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init('gp2protein', fileExt = '.mgi', outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

cmds = []

#
# Get the representative sequence (_Qualifier_key = 615421) for each marker
# if the sequence is:
# Swiss-Prot (logical DB = 13)
# TrEMBL (logical DB = 41
# RefSeq (logical DB = 27 and accID starts with 'NP_' or 'XP_'
#
cmds.append('select mc._Marker_key, ' + \
                   'mc.accID, ' + \
                   'mc._LogicalDB_key ' + \
            'into #markerseq ' + \
            'from ACC_Accession a, SEQ_Marker_Cache mc ' + \
            'where a._MGIType_key = 2 and ' + \
                  '(a._LogicalDB_key in (13,41) or ' + \
                  '(a._LogicalDB_key = 27 and ' + \
                   'a.prefixPart in ("NP_","XP_"))) and ' + \
                  'a._Object_key = mc._Marker_key and ' + \
                  'a.accID = mc.accID and ' + \
                  'mc._Qualifier_key = 615421 and ' + \
                  'mc._Organism_key = 1')

#
# Get the MGI ID for each of the markers.
#
cmds.append('select a.accID "mgiID", ' + \
                   'ms.accID "seqID", ' + \
                   'ms._LogicalDB_key ' + \
            'from ACC_Accession a, #markerseq ms ' + \
            'where a._Object_key = ms._Marker_key and ' + \
                  'a._MGIType_key = 2 and ' + \
                  'a._LogicalDB_key = 1 and ' + \
                  'a.prefixPart = "MGI:" and ' + \
                  'a.preferred = 1 ' + \
            'order by a.accID')

#
# Get the results set.
#
results = db.sql(cmds,'auto')

#
# Write a record to the report for each marker/sequence in the results set.
#
for r in results[1]:
    mgiID = r['mgiID']
    logicalDB = r['_LogicalDB_key']

    #
    # Apply the proper prefix to the seq ID based on the logical DB.
    #
    if logicalDB == 13:
        seqID = 'SWP:' + r['seqID']
    elif logicalDB == 41:
        seqID = 'TR:' + r['seqID']
    else:
        seqID = 'NCBI:' + r['seqID']

    fp.write(mgiID + TAB + seqID + CRT)

reportlib.finish_nonps(fp)
