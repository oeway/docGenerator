#!/usr/bin/env python

import os
from bottle import *
from docGenerator import *
import sys, time
import glob, json, argparse, copy
import webbrowser
    
@route('/js/<filename>')
def js_static(filename):
    return static_file(filename, root='./js')

@route('/img/<filename>')
def img_static(filename):
    return static_file(filename, root='./img')

@route('/css/<filename>')
def img_static(filename):
    return static_file(filename, root='./css')
    
@route('/library/<filename>')
def get_libray_file(filename):
    filename = filename.encode('latin1').decode('utf-8')
    return static_file(filename, root='./library')
    
@route('/template')
def get_template():
    return static_file('Template.doc', root='./')    
    
@route("/")
@view("main")
def hello():
    return dict(title = "docGenerator by OEway", content = "Hello from Python!")

@route("/about")
@view("about")
def hello():
    return dict()
    
@route('/gcode', method='POST')
def gcode_submit_handler():
    global pct,quitFlag
    cwd_temp = os.getcwd()
    print(cwd_temp)
    command_program = request.forms.getunicode('command_program')
    if command_program:
        f = open('.\\Input\\inputdoc.txt','w',encoding= 'UTF-8')
        f.write(command_program)
        f.close()
        generate('.\\Input\\inputdoc.txt')
        return "__ok__"
    else:
        return "disconnected"
    return "__ok__"
 
@get('/upload')
def upload_view():
    return """
        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="text" name="name" />
          <input type="file" name="data" />
          <input type="submit" name="submit" value="upload now" />
        </form>
        """   
 
@post('/upload')
@view("main")
def do_upload():
    name = request.forms.getunicode('name')
    data = request.files.get('data')
    if name is not None and data is not None:
        raw = data.file.read() # small files =.=
        f = open('./Input/'+name,'wb')
        f.write(raw)
        f.close()
        return dict(title = "upload ok", content = "Hello from Python!")
    return "You missed a field."
 
@route('/queue/list')
def library_list_handler():
    # base64.urlsafe_b64encode()
    # base64.urlsafe_b64decode()
    # return a json list of file names
    files = []
    cwd_temp = os.getcwd()
    try:
        os.chdir("library")
        files = glob.glob("*")
    finally:
        os.chdir(cwd_temp)
    return json.dumps(files)
@route('/library/list')
def library_list_handler():
    # return a json list of file names
    file_list = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(".")
        file_list = glob.glob('*')
    finally:
        os.chdir(cwd_temp)
    return json.dumps(file_list)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # open web-browser
    try:
        webbrowser.open_new_tab('http://127.0.0.1:'+str(port))
        pass
    except webbrowser.Error:
        print("Cannot open Webbrowser, please do so manually.")
    #run_with_callback('',port)
    run(host='', port=port, reloader=True)

