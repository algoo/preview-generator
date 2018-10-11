
# Produces a PDF for the SLA passed as a parameter.
# Uses the same file name and replaces the .sla extension with .pdf
#
# usage:
# scribus -g -py to-pdf.py -- file.sla
#
# license:
# (c) MIT Ale Rimoldi

import scribus
import sys

if scribus.haveDoc():
    pdf = scribus.PDFfile()
    pdf.file = sys.argv[1]
    pdf.save()
else:
    print("No file open")
