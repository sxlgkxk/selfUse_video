#!/usr/bin/python3
import json
import os
from os.path import join as path_join

os.chdir('/root/repo/psite/read/tools')
# os.chdir('/home/gkxk/repo/release/read/tools')
read_item_folder='../static/item'
local_item_list_path= '../static/local_item_list.json'
remote_item_list_path= '../static/remote_item_list.json'

with open(local_item_list_path,'r') as f:
    items_list=json.loads(f.read())['list']
    tmp=dict()
    for item in items_list:
        tmp.update({item['name']:item})
    items_dict=tmp

for r, d, f in os.walk(read_item_folder):
    for file in f:
        if os.path.splitext(file)[-1] in ['.epub','.md','.txt','.mobi','.pdf','.docx','.doc']:
            folder=os.path.relpath(r).replace('../static/item/','')
            path=os.path.abspath(path_join(r, file))
            filename=os.path.splitext(os.path.basename(file))[0]
            name=path_join(folder,filename)
            if name not in items_dict:
                os.remove(path)
                print('rm {}'.format(name))

remote_item_list=list()
for item in items_dict.values():
    path=path_join(read_item_folder,item['path'])
    if not os.path.exists(path):
        remote_item_list.append(item['path'])

with open(path_join(remote_item_list_path),'w') as f:
    f.write(json.dumps(remote_item_list))