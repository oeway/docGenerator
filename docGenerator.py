#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    generate xml file with jinja2 from input text file with predefined mark.
    
    
    input file sample:
    *|[Section 1]|:
        content
        *|2[heading 1]|
         content
        *|2[heading 1]|
         content
         content
    *|[Section 2]|:  
    *|[end]|:
    
'''
######First, parse the input file
import re
import shutil
import os
import jinja2

inputFile = 'testdoc.txt'
numberedSection = {'权利要求书':'。',
                    '说明书':'\n',
                    '说明书附图':'\n'}

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
                    #     ns[k].append( (i, m.groups(0)[1].strip()+v) )
                continue
            except:
                pass
            if heading != '':
                if heading in ns[k]:
                    i +=1
                    ns[k][heading].append((i, line.strip()+v))

d['numberedSection'] = ns
#print(ns)
#######Make work directory
templateFileList = []
try:
    shutil.rmtree("./output") 
except:
    print('Delete template directory failed!')
    exit()
try:
    shutil.copytree("./Template","./output")
except:
    print('Copy template directory failed')
    exit()
for dirpath, dirnames, filenames in os.walk('./output'):
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