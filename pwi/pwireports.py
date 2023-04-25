#
# pwireports.py
#
# CGI script for displaying/running custom reports.
# If invoked with no arguments, displays the summary page of available reports.
# 

import sys
import os
import importlib
import cgi

import cgitb
#cgitb.enable()

form = cgi.FieldStorage()

# Returns list of available reports.
def getReportList () :
    reports = []
    fname = "pwireports.txt"
    with open(fname) as fd:
        for line in fd:
            if line.startswith("#"): continue
            # Fields: python name , display name , description , created by , requested by , creation date, argument label
            fields = line[:-1].split("|")
            reports.append({
                "script"       : fields[0],
                "name"         : fields[1],
                "descriptions" : fields[2],
                "createdBy"    : fields[3],
                "requestedBy"  : fields[4],
                "creationDate" : fields[5],
                "argLabel"     : fields[6]
            })
    return reports

#
def runReport () :
    rpt = form["rpt"].value
    if rpt.endswith(".py"):
        script = rpt
        rpt = rpt[:-3]
    else:
        script = rpt + ".py"
    rptInfo = list(filter(lambda d: d["script"] == script,  getReportList()))
    if len(rptInfo) == 1:
        # argument to pass to the script
        arg = None
        if "arg" in form:
            arg = form["arg"].value
        # name to give download file
        fname = None
        if "filename" in form:
            fname = form["filename"].value
        # emit the response header
        header("text-plain", fname)
        # To run the report, we just import it. 
        # To pass an argument, we se sys.argv
        if arg is not None:
            sys.argv = [sys.argv[0], arg]
        # run it!
        importlib.import_module(rpt)
    elif len(rptInfo) == 0:
        errorExit("No report with this name: " + rpt)
    else:
        errorExit("Multiple reports with this name: " + rpt)

#
def header (mimeType, fileName=None) :
    print("Content-Type: " + mimeType)
    if fileName:
        print('Content-Disposition: attachment; filename = "%s"' % fileName)
    print()
#
def errorExit (message) :
    print(message)

#
def main ():
    cmd = form["cmd"].value
    if cmd == "run":
        runReport()
#
main()
