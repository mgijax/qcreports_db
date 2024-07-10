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
def findReport (rpt) :
    rptInfo = list(filter(lambda d: d["script"] == rpt,  getReportList()))
    if len(rptInfo) == 1:
        return rptInfo[0]
    elif len(rptInfo) == 0:
        errorExit("No report with this name: " + rpt)
    else:
        errorExit("Multiple reports with this name: " + rpt)
    
#
def runReport () :
    rpt = form["rpt"].value
    rptInfo = findReport(rpt)
    argLabel = rptInfo.get("argLabel",None)

    # name to give download file
    fname = None
    if "filename" in form:
        fname = form["filename"].value
    # emit the response header
    header("text-plain", fname)

    # Import the module and call its "go" function, passing it the form.
    mod = importlib.import_module(rpt)
    if 'go' in dir(mod):
        mod.go(form)

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
    else:
        raise RuntimeError("Unknown or missing cmd: " + cmd)
#
if __name__ == "__main__":
    main()
