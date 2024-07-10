# test report. Simply prints the form contents.
import sys
import os

def go(form):
    sys.stdout.write("Test \n")
    sys.stdout.write(os.environ['PG_DBSERVER'] + '\n')
    sys.stdout.write(os.environ['PG_DBNAME'] + '\n')
    sys.stdout.write(str(form) + "\n\n")
    
    if 'uploadfile' in form:
        s = form['uploadfile'].value.decode("utf-8")
        sys.stdout.write("Uploaded file:" + s)
