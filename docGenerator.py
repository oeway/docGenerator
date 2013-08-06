#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    generate xml file with jinja2 from input text file with predefined mark.
    
    
    input file sample:
    *|[section1]|:          test
    *|[section2]|:     
    *|[end]|:
    
'''
######First, parse the input file
import re
import shutil
import os
import jinja2

inputFile = 'testdoc.txt'
numberedSection = {'权利要求书':'。',
                    '说明书':'\n'}

s = open(inputFile,encoding='utf-8').readlines()
m = re.findall(r'\[(.+?)\]\|:(.+?)\*\|',"".join(s),flags=re.DOTALL)
d = {key.strip():val.strip() for key, val in m}
ns = {}
for k in numberedSection.keys():
    v = numberedSection[k]
    if k in d:
        ns[k] =[(i,line.strip()+ v) for i,line in enumerate(d[k].split(v)) if line.strip() != '' ]

d['numberedSection'] = ns
print(d)
#######Make work directory
templateFileList = []
try:
	shutil.rmtree("./tmp") 
except:
	print('Delete template directory failed!')
	exit()
try:
	shutil.copytree("./Template","./tmp")
except:
	print('Copy template directory failed')
	exit()
for dirpath, dirnames, filenames in os.walk('./tmp'):
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