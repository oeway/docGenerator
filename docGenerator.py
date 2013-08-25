#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (C) 2013 - oeway007@gmail.com

    generate xml file with jinja2 from input text file with predefined format.
    Originally used for Chinese patent archive.
    
    
'''
######First, parse the input file
import re
import shutil
import os
import jinja2
import zipfile
import datetime
from PIL import Image
imageWidth = 160
patentBigTitle = "专利申请文件V2.0"
contentDict = {}
infoFeild ={}


instructLst = ['技术领域','背景技术','专利内容','附图说明','具体实施方式']

imageSectionPath = {'说明书附图':'100003',
                '摘要附图':'100005'}

imageNameBase = '1308041747'


#clear input directory
filelist=[]
rootdir="./Input"
filelist=os.listdir(rootdir)
for f in filelist:
    filepath = os.path.join( rootdir, f )
    if os.path.isfile(filepath):
        os.remove(filepath)
        print(filepath+" removed!")
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath,True)
        print("dir "+filepath+" removed!")

def init():
    global infoFeild,contentDict
    infoFeild ={
        '专利类型':'',
        '专利名称':'',
        '第一发明人':'',
        '身份证号码':'',
        '其他发明人':[],
        '第一申请人':'',
        '其他申请人':[],  
    }
    contentDict = {
        'root':[],
        patentBigTitle:infoFeild,
        '说明书摘要':[],
        '摘要附图':[],
        '权利要求书':[],
        '说明书':[],
        '技术领域':[],
        '背景技术':[],
        '专利内容':[],
        '附图说明':[],
        '具体实施方式':[],
        '说明书附图':[]
    }
    
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
imageIndex = 0
def addImage(img,sec):
    global imageIndex
    img = img.strip()
    imageIndex +=10
    fileName, fileExtension = os.path.splitext(img)
    imgName = imageNameBase + str(imageIndex)+fileExtension
    imgDict = {}
    imgDict['type'] = 'image'
    imgDict['img-format'] = fileExtension.strip('.')
    im = Image.open(os.path.join('Input',img))
    imgDict['width'] = imageWidth
    imgDict['height'] = int(1.0*im.size[1]*imgDict['width']/im.size[0])
    #print(im.size)
    imgDict['content'] = imgName
    shutil.copy (os.path.join('Input',img),  os.path.join('Output',imageSectionPath[sec],imgName))
    if os.path.isfile (os.path.join('Output',imageSectionPath[sec],imgName)): print("Copy File Success")
    return imgDict

def generate(inputFileName):
    global infoFeild,contentDict
    init()
    f = open(inputFileName,encoding='utf-8')
    secName = 'root'
    for line in f:
        print(line)
        if len(line)<100:#maybe its a section title
            maybeTitle = line.replace(' ','').strip()
            if maybeTitle in contentDict:
                secName = maybeTitle
                continue
        currentSection = contentDict[secName]
        if type(currentSection) == type({}): #dict
            tmp = line.split()
            if len(tmp)>1:
                if tmp[0] in currentSection:
                    if type(currentSection[tmp[0]]) == type([]): #list
                        currentSection[tmp[0]] = [{'index':i,'content':tmp[i]} for i in range(len(tmp)) if i>0]
                    else:
                        currentSection[tmp[0]] = tmp[1]
                    contentDict[tmp[0]] = currentSection[tmp[0]] # add to main dict
        else: # content
            if line.strip() != "":
                currentSection.append(line.strip())
    print([i+str(len(contentDict[i])) for i in contentDict.keys() if contentDict[i] != []])
    #print(contentDict['权利要求书'])
    rights = []
    currentRight = ''
    i = 0
    for line in contentDict['权利要求书']:
        currentRight +=line
        if line.endswith('。'):
            i +=1
            rights.append({'index':i,'content':currentRight})
            currentRight = ''
    contentDict['权利要求书'] = rights
    contentDict['权利要求项数'] = len(rights)
    #print(contentDict['权利要求书'])
    i = 0
    for sec in instructLst:
        tmpLst = []
        for line in contentDict[sec]:
            if line.endswith('。'):
                i +=1
                tmpLst.append({'index':i,'content':line})
            else:
                tmpLst.append({'index':-1,'content':line})
        contentDict[sec] = tmpLst
        #print(contentDict[sec])    
    da = datetime.date.today()
    contentDict['日期'] = {"年":da.year,"月":da.month,"日":da.day}
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

        
    for sec in imageSectionPath:
        imgLst = []
        for i,img in enumerate(contentDict[sec]):
            d = addImage(img,sec)
            d['index'] = i+1
            imgLst.append(d)
        contentDict[sec] = imgLst

    templateFileList = []
    for dirpath, dirnames, filenames in os.walk('./Output'):
        for filename in filenames:
            fullpath = os.path.join(dirpath,filename)
            if '.xml' in filename:
                templateFileList.append((dirpath,filename))

    #######Second, fill the template
    for dirpath, TEMPLATE_FILE in templateFileList:
        try:
            templateLoader = jinja2.FileSystemLoader( searchpath= dirpath , encoding='utf-8')
            templateEnv = jinja2.Environment( loader=templateLoader )
            template = templateEnv.get_template( TEMPLATE_FILE)
            outputText = template.render( contentDict )
        #######Save output file
            f=open(os.path.join(dirpath,TEMPLATE_FILE) ,'w',encoding='utf-8')
            f.write(outputText)
            f.close() 
            print(TEMPLATE_FILE + '  done!')
        except:
            os.remove(os.path.join(dirpath,TEMPLATE_FILE))
            print("Error when process " + TEMPLATE_FILE)


    #######Make Archive
    filename = 'library\\' + contentDict[patentBigTitle]['专利名称']+'.zip'
    directory = 'Output'
    toZip(directory, filename)
    print('Done!')

    
if __name__ == '__main__':
    inputFileName = './Input/inputDoc.txt'
    generate(inputFileName)
