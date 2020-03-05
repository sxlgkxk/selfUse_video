#!/usr/bin/python3
from flask import Flask,make_response,request,jsonify
from flask import render_template,redirect,session
import json
import os
import time
from os.path import exists as path_exists
from os.path import join as path_join
import re
import logging
import sys
import subprocess as sp
import multiprocessing as mp
import math
from moviepy.editor import VideoFileClip
import redis

app = Flask(os.path.basename(os.getcwd()))
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key='sxlgkxk'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
item_list,category_list=list(),list()
category2pages=dict()
N_PER_PAGE=50
SITE_PORT=5005
SITE_NAME=os.path.basename(os.getcwd())
stat=dict()
stat['name']=SITE_NAME

@app.route('/')
@app.route('/c/index')
def index():
    page=request.args.get('page')
    if not page:
        page=1
    else:
        page=int(page)
    return render_template('index.html',stat=stat,item_list=item_list[(page-1)*N_PER_PAGE:page*N_PER_PAGE],
                           category_list=category_list,
                           category='/',
                           page=page,
                           path='index',
                           pages=math.ceil(len(item_list)/N_PER_PAGE))


@app.route('/c/<path:name>')
def view_category(name):
    page=request.args.get('page')
    if not page:
        page=1
    else:
        page=int(page)
    pattern=r'^{}'.format(name.replace('[','\[').replace(']','\]').replace('(','\(').replace(')','\)'))
    sub_category_list=[x for x in  category_list if re.match(pattern,x['name']) and x['size']]
    _item_list=[x for x in item_list if re.match(pattern,x['category'])]
    pages=math.ceil(len(_item_list)/N_PER_PAGE)
    _item_list=_item_list[(page-1)*N_PER_PAGE:page*N_PER_PAGE]
    return render_template('index.html',stat=stat,
                           item_list=_item_list,
                           #item_list=[x for x in item_list if x['category']==name][(page-1)*N_PER_PAGE:page*N_PER_PAGE],
                           # category_list=[x for x in  category_list if re.match('^{}/'.format(name),x['name']) or re.match('^{}/'.format(x['name']),name) or name==x['name']],
                           category_list=category_list,
                           cur_category=name,
                           path=name,
                           page=page,
                           pages=pages)


@app.route('/v/<path:name>')
def view_item(name):
    return render_template('item.html',stat=stat,
                           filename=os.path.basename(name),
                           category_list=category_list,
                           cur_category=os.path.dirname(name.replace('static/item/','')),
                           path=name)

def refreshFunc():
    global item_list,category_list,category2pages

    db = redis.Redis()
    if db.get('video_refreshing'):
        return
    db.set('video_refreshing','running')
    db.expire('video_refreshing', 60*30)

    with open('static/item_list.json','r') as f:
        tmp=json.loads(f.read())
        old_item_list=tmp['list']
        old_category_list=tmp['category_list']
    new_category_list=list()
    new_item_list=list()
    item_dict=dict()
    for item in old_item_list:
        item_dict[item['name']]=item
    category_dict=dict()

    for r, d, f in os.walk('static/item',followlinks=True):
        if os.path.basename(r)[0] in ['.', '_']:
            logging.info("folder[0] is '.' or '_', continue")
            continue
        category = r.replace('static/item/', '')
        if category == 'static/item':
            continue
        if category not in new_category_list:
            new_category_list.append(category)
            category_dict[category] = 0
        for file in f:
            if os.path.basename(file)[0] == '.':
                logging.info("filename[0] is '.' or '_', continue")
                continue
            if os.path.splitext(file)[-1] in ['.mp4','.flv','.webm']:
                category_dict[category]+=1
                path = path_join(r, file)
                mtime = os.stat(path).st_mtime
                filename = os.path.splitext(os.path.basename(file))[0]
                name=path_join(category,filename)

                if name in item_dict:
                    if item_dict[name]['mtime'] == mtime:
                        new_item_list.append(item_dict[name])
                        continue
                safe_path=path.replace(' ','\ ')\
                        .replace("'","\'")\
                        .replace('"','\"')\
                        .replace('*','\*')\
                        .replace('?','\?')\
                        .replace('\\','\\\\')\
                        .replace('~','\~')\
                        .replace('`','\`')\
                        .replace('!','\!')\
                        .replace('#','\#')\
                        .replace('$','\$')\
                        .replace('&','\&')\
                        .replace('|','\|')\
                        .replace('{','\{')\
                        .replace('}','\}')\
                        .replace('(','\(')\
                        .replace(')','\)')\
                        .replace(';','\;')\
                        .replace('<','\<')\
                        .replace('>','\>')\
                        .replace('^','\^')
                clip = VideoFileClip(path)
                start=300
                duration=10
                if clip.duration<310:
                    start=0
                    duration=clip.duration
                status=sp.getoutput('ffmpeg -i {gif} -ss {start} -t {duration} -vf scale=100:-1 -f gif {gif}.gif -y'.format(start=start, gif=safe_path, duration=duration))
                item = {'name': name,
                        'filename':filename,
                        'category': category,
                        'path':path,
                        'abbr':'',
                        'mtime': mtime}
                print('use new \'{}\''.format(name))
                new_item_list.append(item)
    new_item_list.sort(key=lambda x: x['mtime'],reverse=True)
    item_list=new_item_list
    category_list=[{'name':x,'size':category_dict[x]} for x in new_category_list]
    for name in category_dict:
        category_dict[name]=math.ceil(category_dict[name]/N_PER_PAGE)
    category2pages=category_dict
    category_list.sort(key=lambda x: x['name'])
    with open('static/item_list.json','w') as f:
        f.write(json.dumps({'list':item_list,'category_list':category_list}))
    db.delete('video_refreshing')

@app.route('/search')
def search():
    keys=request.args['keys'].split(' ')
    itemlist=item_list
    for key in keys:
        itemlist=[x for x in itemlist if key in x['name'] or key in x['abbr']]

    return jsonify(itemlist=itemlist)

def main_processor():
    while True:
        time.sleep(1)
        status=sp.getoutput('curl http://127.0.0.1:{}/refresh'.format(SITE_PORT))

@app.route('/refresh')
def refresh():
    refreshFunc()
    return redirect('/')

def app_init():
    p=mp.Process(target=main_processor)
    p.start()
    db=redis.Redis()
    db.delete('video_refreshing')
    refreshFunc()

app_init()

if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0",port=SITE_PORT,use_reloader=False)
