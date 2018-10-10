#! /usr/bin/env python
import requests
from BeautifulSoup import BeautifulSoup
import os
import config
import csv
import re
import glob

def extractPages (session):
    r = session.get(config.URL)
    soup = BeautifulSoup(r.text)

    colleges=soup.findAll('a',{'class':'link-results'})
    for eachcollege in colleges:
        #print eachcollege['href']
        fileurl = ''.join([config.BASEURL,eachcollege['href']])
        #print fileurl
        response = requests.get(fileurl)
        #print response.headers
        filename = response.headers['Content-Disposition'].split('; ')[1].split('=')[1].strip('"')
        with open(filename,'wb') as fp:
            fp.write(response.content)
            print "Downloaded ", filename
    return True

def parseHTMLFile(path,outCSV):
    f = open(path, 'r')
    r = f.read()
    f.close()
    rootSoup = BeautifulSoup(r)
    texts = rootSoup.findAll("p")
    texts = [x for x in texts if x.text != '&#160;']
    texts = [x for x in texts if x.text != 'Controller of Examinations']
    texts = [x.text for x in texts]
    #texts = [x for x in texts where x.replace('&#160','')]
    texts = [x for x in texts if x != '*TBP -To Be Published Soon']
    texts = texts[:-1]
    marklist = []
    totalLines = len(texts)
    #for x in texts:
        #print x
    #DBG: Biju
    #print "Total lines = ", totalLines
    collegeName = texts[2]
    collegeName = collegeName.replace('Exam Centre: ', '')
    collegeName = collegeName.replace('&amp;','&')
    collegeName = collegeName.replace('&#160;','')
    collegeName = collegeName.replace(',','')
    #DBG: Biju
    #print "College Name is: ", collegeName
    examName = texts[3]
    rYr,rSem = re.match(".*Exam.*([0-9]{2}) \(S([0-9]) Result\)", examName).groups()
    #print "First group: ", rYr, "Second group: ", rSem
    #print "Reg Year is: ",int(rYr) - int(rSem) / 2
    regYr = int(rYr) - int(rSem) / 2
    i = 4
    while (i < totalLines):
        if((i+2 < totalLines) and (texts[i+1] == 'Course Code')
			and (texts[i+2] == 'Course')):
            branchName = texts[i]
            branchName = branchName.replace('[Full Time]','')
            branchName = branchName.replace('&amp;','&')
            #DBG: Biju
            #print "Branch is ", branchName
            i = i + 3
            #Initialize the course list
            courseList = []
            while texts[i] != 'Register No':
                courseList.append(texts[i])
                i = i + 2
                #Skip one more line for multiline course names
                if not (re.match("[A-Z]{2}[0-9]{3}", texts[i])
                   or (texts[i] == 'Register No')):
                    i = i + 1
            #DBG: Biju
            #print "Course List is: ", courseList
            #Skip Register No, Course Code (Grade) lines
            i = i + 2
        regNo = texts[i]
        i = i + 1
        #DBG: Biju
        #print "Register No. is: ", regNo
        #Is this register number to be processed?
        expr = "L?[A-Z]{3}"+str(regYr)+"[A-Z]{2}[A-Z]?[0-9]{3}"
        #print "Reg No. reg expr is: ", expr, "Regular is: ", "L?[A-Z]{3}16[A-Z]{2}[A-Z]?[0-9]{3}"
        if re.match(expr, regNo):
        #if re.match("L?[A-Z]{3}16[A-Z]{2}[A-Z]?[0-9]{3}", regNo):
            #print "Register No. is: ", regNo
            score = texts[i]
            i = i + 1
            if i < totalLines and not (re.match("L?[A-Z]{3}1[0-9][A-Z]{2}[A-Z]?[0-9]{3}", texts[i]) or
                    (i+3 < totalLines and texts[i+1] == 'Course Code' and texts[i+2] == 'Course')):
                score = score + texts[i]
                i = i + 1
            #Now process the score
            #lstScore = [i for i in s.strip(')').split('(') for s in score.split(',')] 
            #score = score.strip(' ')
            lstScore = [j for s in score.split(',') for j in s.strip(')').strip(' ').split('(') ] 
            #print "Score in new form is: ", lstScore
            temp = [regNo]+[branchName]+[collegeName]+lstScore
            #print "temp is: ", temp
            marklist.append(temp)
            #print "Score is: ", score
        else:
            i = i + 1
            if not ((i < totalLines and re.match("L?[A-Z]{3}1[0-9][A-Z]{2}[A-Z]?[0-9]{3}", texts[i])) or
                    (i+3 < totalLines and texts[i+1] == 'Course Code' and texts[i+2] == 'Course')):
              i = i + 1
    with open(outCSV, "ab") as f:
        writer = csv.writer(f)
        writer.writerows(marklist)


if __name__ == '__main__':
    if not os.path.exists(config.DIRECTORY):
        os.makedirs(config.DIRECTORY)
    os.chdir(config.DIRECTORY)
    session = requests.Session()
    options = extractPages (session)

    #Process the pdf files
    pdfFiles = sorted(glob.glob("*.pdf"))
    for file in pdfFiles:
        print "Processing file: ", file
        cmd = config.PDFCONVERTER+file
        htmlFile = file.replace('.pdf','-html.html')
        #Delete the html file if it exists
        if os.path.isfile(htmlFile):
            os.remove(htmlFile)
        os.system(cmd)
        parseHTMLFile(htmlFile, "./Marklist.csv")
    #print("Starting KGU EXTERNALS Extraction BOT")
    #parseFile("result_RET.txt")
    #parseHTMLFile("result_RET-html.html", "Marklist.csv")
    #parseHTMLFile("result_RETs5-html.html", "Marklist.csv")
    #print "Successful!"
