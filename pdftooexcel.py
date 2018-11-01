import os
import re
import csv
import math
from datetime import datetime

megaarray=[]#to store every row extracted from text file

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
        if re.match("L?[A-Z]{2}[0-9]{3}",fileLines[i+3]):
            striplist=[]
            for i in fileLines[i+3].split(','):
                striplist.append(i.strip())
            marksblock = marksblock +striplist
            striplist=[]
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
        megaarray.append(row)
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

br = megaarray[0][2] # init branch
sublist = {}         # init subjectlists in input file
studentcount = 0
semsubject = []     #subjects of surrent sem
for r in megaarray:
    if r[2] == br:
        studentcount += 1
        i = 3
        while i < len(r):
            if r[i] in sublist.keys():
                sublist[r[i]] = int(sublist.get(r[i]))+1
            else:
                sublist[r[i]] = 1
            i += 2
    else:
        offset = studentcount / 3
        temp = []
        for key, value in sublist.items():
            if value > offset:
                temp.append(key)
        br = r[2]
        studentcount = 0
        sublist = {}
        semsubject.append(temp)
offset = studentcount / 3
temp = []
for key, value in sublist.items():
    if value > offset:
        temp.append(key)
semsubject.append(temp)
check=0
br = megaarray[0][2]
branchno=0
sub = semsubject[branchno]
stuarray= []
actualarray = []
for i in megaarray:
    stuarray = i[:3]
    if i[2] == br:
        for elem in sub:
            check=0
            stuarray.append(elem)
            count = 3
            while count < len(i):
                if elem.strip() in i[count].strip():
                    check=1
                    stuarray.append(i[count+1])
                    count+=1
                    break
                else:
                    count+=1
            if check==0:
                stuarray.append('')
    else:
        br = i[2]
        branchno += 1
        sub = semsubject[branchno]
        if i[2] == br:
            for elem in sub:
                check=0
                stuarray.append(elem)
                count = 3
                while count < len(i):
                    if elem.strip() == i[count].strip():
                        check = 1
                        stuarray.append(i[count + 1])
                        count += 2
                    else:
                        count += 1
                if check == 0:
                    stuarray.append('')
    actualarray.append(stuarray)
    stuarray = []
f = open("improvised.csv", "wb")
writer = csv.writer(f)
writer.writerows(actualarray)
f.close()
