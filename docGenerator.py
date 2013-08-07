#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    generate xml file with jinja2 from input text file with predefined mark.
    
    
    input file sample:
    ====Section 1====
        root
        content
        ----heading 1----
         content
        -----heading 1----
         content
         content
    ====Section 2==== 
    ====end====
    
'''
######First, parse the input file
import re
import shutil
import os
import jinja2
import zipfile

inputFile = './Input/testdoc.txt'
numberedSection = {'权利要求书':'。',
                    '说明书':'。\n',
                    '说明书附图':'\n',
                    '其他发明人':'\n',
                    '其他申请人':'\n'}

imageSectionPath = {'说明书附图':'100003',
                '摘要附图':'100005'}

imageNameBase = '1308041747'
s = open(inputFile,encoding='utf-8').readlines()
m = re.findall(r'==(.+?)====\n(.+?)\n==',"".join(s),flags=re.DOTALL)
d = {key.strip().replace('=',''):val.strip() for key, val in m if key.strip()!= '' or val.strip()!=""}

ns = {}
for k in numberedSection.keys():
    v = numberedSection[k]
    if k in d:
        #ns[k] =[(i,line.strip()+ v) for i,line in enumerate(d[k].split(v)) if line.strip() != '' ]
        i = 0
        ns[k] = {}
        heading = "root"
        ns[k][heading] = []
        for line in d[k].split(v):
            if line.strip() == '':
                continue
            m = re.match(r'----(.+?)----',line,flags=re.DOTALL)
            try:
                if len(m.groups(0)) > 0:
                    heading = m.groups(0)[0].strip()
                    ns[k][heading] = []
                    #print(m.groups(0))
                    # if m.groups(0)[1].strip() != "":
                    #     i +=1
                    #     ns[k].append( {'index':i,'type':'text', 'value':m.groups(0)[1].strip()+v} )
                continue
            except:
                pass
            if heading != '':
                if heading in ns[k]:
                    i +=1
                    ns[k][heading].append({'index':i,'type':'text','content':line.strip()+v})
d['numberedSection'] = ns

#######Make work directory
try:
    shutil.rmtree("./Output") 
except:
    print('Delete template directory failed!')
try:
    shutil.copytree("./Template","./Output")
except:
    print('Copy template directory failed')
    exit()

imageIndex = 0        
for sec in imageSectionPath.keys():
    images = d[sec].split('\n')
    imgLst = []
    for img in images:
        imageIndex +=10
        fileName, fileExtension = os.path.splitext(img)
        imgName = imageNameBase + str(imageIndex)+fileExtension
        imgDict = {}
        imgDict['type'] = 'image'
        imgDict['img-format'] = fileExtension.strip('.')
        imgDict['width'] = 102
        imgDict['content'] = imgName
        if sec in d:
            d[sec] = imgName
        imgLst.append(imgDict)
        shutil.copy (os.path.join('Input',img),  os.path.join('Output',imageSectionPath[sec],imgName))
        if os.path.isfile (os.path.join('Output',imageSectionPath[sec],imgName)): print("Copy File Success")
    if sec in d['numberedSection']:
        d['numberedSection'][sec]['root'] = imgLst

templateFileList = []

for dirpath, dirnames, filenames in os.walk('./Output'):
    for filename in filenames:
        fullpath = os.path.join(dirpath,filename)
        if '.xml' in filename:
            templateFileList.append((dirpath,filename))

#######Second, fill the template
for dirpath, TEMPLATE_FILE in templateFileList:
    templateLoader = jinja2.FileSystemLoader( searchpath= dirpath , encoding='utf-8')
    templateEnv = jinja2.Environment( loader=templateLoader )
    template = templateEnv.get_template( TEMPLATE_FILE)
    outputText = template.render( d )
#######Save output file
    f=open(os.path.join(dirpath,TEMPLATE_FILE) ,'w',encoding='utf-8')
    f.write(outputText)
    f.close() 
    print(TEMPLATE_FILE + '  done!')


#######Make Archive

def toZip( file, filename):
    zip_file = zipfile.ZipFile(filename, 'w')
    if os.path.isfile(file):
        zip_file.write(file)
    else:
        addFolderToZip(zip_file, file)
    zip_file.close()

def addFolderToZip( zip_file, folder): 
    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path):
            print('File added: ' + str(full_path))
            zip_file.write(full_path)
        elif os.path.isdir(full_path):
            print ('Entering folder: ' + str(full_path))
            addFolderToZip(zip_file, full_path)
filename = 'Output.zip'
directory = 'Output'
toZip(directory, filename)