#!/usr/bin/python3
import json
import os
import sys
from os.path import join as path_join
import subprocess as sp
import markdown
import requests
import shutil
import re
import time
import redis
import logging

status=requests.get('http://www.baidu.com').status_code
if status != 200:
    sys.exit()

os.chdir('/home/gkxk/repo/release/read/tools')

logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s:%(message)s'
        )
db=redis.Redis()
if db.get('read_uploading'):
    sys.exit()
db.set('read_uploading','running')
db.expire('read_uploading',60*30)
#db.expire('read_uploading',1)

is_changed=False
item_folder=os.path.abspath('../static/item')
local_item_list_path=os.path.abspath('../static/local_item_list.json')
remote_item_list_path=os.path.abspath('../static/remote_item_list.json')
old_items,new_items,folder_list=list(),list(),list()

with open(local_item_list_path, 'r') as f:
    content=json.loads(f.read())
    old_items=content['list']
    old_folder_list=content['folder_list']
    tmp=dict()
    for item in old_items:
        tmp.update({item['name']:item})
    old_items_dict=tmp

for r, d, f in os.walk(item_folder):
    if os.path.basename(r)[0] in ['.','_']:
        logging.info("folder[0] is '.' or '_', continue")
        continue
    for file in f:
        if os.path.basename(file)[0]=='.':
            logging.info("filename[0] is '.' or '_', continue")
            continue
        if os.path.splitext(file)[-1] in ['.epub','.md','.txt','.mobi','.pdf','.docx','.doc']:
            folder=os.path.relpath(r).replace('../static/item/','')

            if not folder in old_folder_list:
                cmd = 'ssh root@108.160.135.157 "/root/repo/psite/read/tools/check.py {}"'.format(
                    r.replace('/home/gkxk/repo/release/read', '/root/repo/psite/read')
                              .replace(' ', '\ ')
                              .replace('(','\(')
                              .replace(')', '\)')
                              .replace("'", "\\'"))
                status = sp.getoutput(cmd)
                logging.info("create '{}' if not existed status: {}".format(os.path.relpath(r), status))
                print("create '{}' if not existed status: {}".format(os.path.relpath(r), status))
                old_folder_list.append(folder)

            if not folder in folder_list:
                folder_list.append(folder)
            path=path_join(folder, file)
            filename=os.path.splitext(os.path.basename(file))[0]
            name=path_join(folder,filename)
            mtime=os.stat(path_join(r,file)).st_mtime

            if name in old_items_dict:
#                if old_items_dict[name]['mtime']==mtime:
                new_items.append(old_items_dict[name])
                print('use old \'{}\''.format(name))
                continue

            item={'name':name,
                  'folder':folder,
                  'path':path,
                  'mtime':mtime}
            print('use new \'{}\''.format(name))
            logging.info('use new \'{}\''.format(name))
            is_changed=True
            path=os.path.join(item_folder,path)\
                              .replace(' ', '\ ')\
                              .replace('(','\(')\
                              .replace(')', '\)')\
                              .replace("'", "\\'")
            cmd='scp {} root@108.160.135.157:"{}"'.format(path, path.replace('/home/gkxk/repo/release/read',
                                                                                    '/root/repo/psite/read'))
            status=sp.getoutput(cmd)
            print('scp cmd "{}" status: "{}"'.format(cmd,status))
            new_items.append(item)
            with open(local_item_list_path, 'w') as f:
                f.write(json.dumps({'list':new_items,'folder_list':folder_list}))

new_items.sort(key=lambda x:x['mtime'],reverse=True)

with open(local_item_list_path, 'w') as f:
    f.write(json.dumps({'list':new_items,'folder_list':folder_list}))

if is_changed:
    status=sp.getoutput('scp "{}" root@108.160.135.157:"{}"'.format(local_item_list_path, local_item_list_path.replace('/home/gkxk/repo/release/read',
                                                                                    '/root/repo/psite/read').replace(' ', '\ ')
                              .replace('(','\(')
                              .replace(')', '\)')
                              .replace("'", "\\'")))
    os.chdir('/home/gkxk/repo/git/sxlgkxk.github.io')
    status = sp.getoutput('git checkout hexo')
    status = sp.getoutput('git add * && git commit -m "add text" && git push origin hexo')
    status = sp.getoutput('curl http://108.160.135.157:5003/refresh')

while True:
    status=sp.getoutput('ssh root@108.160.135.157 "python3 /root/repo/psite/read/tools/remote.py"')
    status = sp.getoutput('scp root@108.160.135.157:"{}" "{}"'.format(remote_item_list_path.replace('/home/gkxk/repo/release/read',
                                                                                       '/root/repo/psite/read'),remote_item_list_path))
    with open(remote_item_list_path,'r') as f:
        remote_item_list=json.loads(f.read())
    if remote_item_list == []:
        break
    for name in remote_item_list:
        path = path_join(item_folder, name)\
                              .replace(' ', '\ ')\
                              .replace('(','\(')\
                              .replace(')', '\)')\
                              .replace("'", "\\'")
        cmd='scp {} root@108.160.135.157:"{}"'.format(path,path.replace('/home/gkxk/repo/release/read','/root/repo/psite/read'))
        status = sp.getoutput(cmd)
        print('fix lack cmd "{}" status: "{}"'.format(cmd,status))
    status = sp.getoutput('curl http://108.160.135.157:5003/refresh')
    status=sp.getoutput('scp "{}" root@108.160.135.157:"{}"'.format(local_item_list_path, local_item_list_path.replace('/home/gkxk/repo/release/read',
                                                                                    '/root/repo/psite/read').replace(' ', '\ ')
                              .replace('(','\(')
                              .replace(')', '\)')
                              .replace("'", "\\'")))

    db.delete('read_uploading')
