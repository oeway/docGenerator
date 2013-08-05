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

inputFile = 'testdoc'
numberedSection = {'说明书':'。'}


s = open(inputFile).readlines()
m = re.findall(r'\|\[(.+?)\]\|:(.+?)\*',"".join(s),flags=re.DOTALL)
d = {key.strip():val.strip() for key, val in m}
ns = {}
for k in numberedSection.keys():
    v = numberedSection[k]
    if k in d:
        ns[k] =[(i,line.strip()+ v) for i,line in enumerate(d[k].split(v)) if line.strip() != '' ]
print(ns)
d['numberedSection'] = ns


#######Second, fill the template
import jinja2
templateLoader = jinja2.FileSystemLoader( searchpath="." )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPLATE_FILE = "00001.xml"
template = templateEnv.get_template( TEMPLATE_FILE )
outputText = template.render( d )