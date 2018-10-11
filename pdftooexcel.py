import os
import re
import csv
import math
from datetime import datetime
currentyear = datetime.now().year % 100
os.system("pdftotext -nopgbrk input1.pdf")
clgnamefound = 0
batchfound = 0
f = open("input1.txt", 'r')
fileLines = f.readlines()
f.close()
f = open("output.csv", "wb")
writer = csv.writer(f)
maxlength = len(fileLines)
for i in range(0, maxlength):
    if fileLines[i] == "\n":
        continue
    elif clgnamefound == 0:
        if "Exam Centre" in fileLines[i]:
            clgnamefound = 1
            collagename = fileLines[i].replace('Exam Centre: ', '')
    elif "Course Code\n" == fileLines[i]:  # exact match ==
        branch = fileLines[i-1].replace('[Full Time]', '')
    elif batchfound == 1 and re.match("L?[A-Z]{3}"+str(batch)+"L?[A-Z]{2}[A-Z]?[0-9]{3}", fileLines[i]):
        regno = fileLines[i]
        marksblock = fileLines[i+2].split(',')
        try:
            marksblock.remove("\n")
        except:
            pass
        marks = []
        for i in marksblock:
            marks.append(i.split('(')[0])
            marks.append((i.split('(')[1].replace(")", "")))
        marks[-1] = marks[-1].replace('\n', '')
        row = [regno.strip()]+[collagename.strip()]+[branch.strip()]+marks
        writer.writerows([row])
    elif "B.Tech" in fileLines[i]:
        lines = fileLines[i].split()
        for i in lines:
            if re.match("L?S[0-8]", i):
                sem = int(i.replace('S', ''))
                sem = int((math.ceil(sem/2)))
                batch = currentyear - sem
                batchfound = 1
f.close()
