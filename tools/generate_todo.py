#!/usr/bin/python3

import os
import json
import sys
import shutil
import re
import subprocess as sp
import time
import requests

status=requests.get('http://www.baidu.com').status_code
if status != 200:
    sys.exit()

path_exist=os.path.exists
path_join=os.path.join

md_path='/home/gkxk/repo/release/blog/static/item/todo/timetable'
t=time.localtime(time.time())
link='http://108.160.135.157:5000'

# with open('/home/gkxk/repo/release/timetable/static/item/timetable/day-template.md','r') as f:
#     day_template=f.read()

##### day #####
# file_day=time.strftime("day-%Y-%m-%d.md",t)
year,month,day=time.strftime('%Y',t),time.strftime('%m',t),time.strftime('%d',t)
# if not path_exist(path_join(md_path,file_day)):
#     with open(path_join(md_path,file_day),'w') as f:
#         f.write(day_template.format(year=year,month=month,day=day,link=link))





##### month achievement #####
# file_month=time.strftime("month-achievement-%Y-%m.md",t)
# if not path_exist(path_join(md_path,file_month)):
#     with open('/home/gkxk/repo/release/timetable/static/item/.template/month-achievement-template.md','r') as f:
#         month_template=f.read()
#     with open(path_join(md_achievement_path,file_month),'w') as f:
#         f.write(month_template.format(year=year,month=month,link=link))

##### year achievement #####
# file_year=time.strftime("year-achievement-%Y.md",t)
# if not path_exist(path_join(md_path,file_year)):
#     with open('/home/gkxk/repo/release/timetable/static/item/.template/year-achievement-template.md','r') as f:
#         year_template=f.read()
#     with open(path_join(md_achievement_path,file_year),'w') as f:
#         f.write(year_template.format(year=year,link=link))



##### month moneyflow #####
# file_month=time.strftime("month-moneyflow-%Y-%m.md",t)
# if not path_exist(path_join(md_path,file_month)):
#     with open('/home/gkxk/repo/release/timetable/static/item/.template/month-moneyflow-template.md','r') as f:
#         month_template=f.read()
#     with open(path_join(md_path,file_month),'w') as f:
#         f.write(month_template.format(year=year,month=month,link=link))

##### year moneyflow #####
# file_year=time.strftime("year-moneyflow-%Y.md",t)
# if not path_exist(path_join(md_path,file_year)):
#     with open('/home/gkxk/repo/release/timetable/static/item/.template/year-moneyflow-template.md','r') as f:
#         year_template=f.read()
#     with open(path_join(md_path,file_year),'w') as f:
#         f.write(year_template.format(year=year,link=link))



##### month dopamine #####
# file_month=time.strftime("month-dopamine-%Y-%m.md",t)
# if not path_exist(path_join(md_path,file_month)):
#     with open('/home/gkxk/repo/release/timetable/static/item/.template/month-dopamine-template.md','r') as f:
#         month_template=f.read()
#     with open(path_join(md_path,file_month),'w') as f:
#         f.write(month_template.format(year=year,month=month,link=link))

##### year dopamine #####
# file_year=time.strftime("year-dopamine-%Y.md",t)
# if not path_exist(path_join(md_path,file_year)):
#     with open('/home/gkxk/repo/release/timetable/static/item/.template/year-dopamine-template.md','r') as f:
#         year_template=f.read()
#     with open(path_join(md_path,file_year),'w') as f:
#         f.write(year_template.format(year=year,link=link))



##### month #####
file_month=time.strftime("month-%Y-%m.md",t)
if not path_exist(path_join(md_path,file_month)):
    with open('/home/gkxk/repo/release/blog/static/item/todo/timetable/_template/month-template.md','r') as f:
        month_template=f.read()
    with open(path_join(md_path,file_month),'w') as f:
        f.write(month_template.format(year=year,month=month,link=link))

##### year #####
file_year=time.strftime("year-%Y.md",t)
if not path_exist(path_join(md_path,file_year)):
    with open('/home/gkxk/repo/release/blog/static/item/todo/timetable/_template/year-template.md','r') as f:
        year_template=f.read()
    with open(path_join(md_path,file_year),'w') as f:
        f.write(year_template.format(year=year,link=link))




##### day+1 #####
# t=time.localtime(time.time()+60*60*24)
# file_plus1=time.strftime("day-%Y-%m-%d.md",t)
# year,month,day=time.strftime('%Y',t),time.strftime('%m',t),time.strftime('%d',t)

# if not path_exist(path_join(md_path,file_plus1)):
#     with open(path_join(md_path,file_plus1),'w') as f:
#         f.write(day_template.format(year=year,month=month,day=day,link=link))

##### day+2 #####
# t=time.localtime(time.time()+60*60*24*2)
# file_plus2=time.strftime("day-%Y-%m-%d.md",t)
# year,month,day=time.strftime('%Y',t),time.strftime('%m',t),time.strftime('%d',t)

# if not path_exist(path_join(md_path,file_plus2)):
#     with open(path_join(md_path,file_plus2),'w') as f:
#         f.write(day_template.format(year=year,month=month,day=day,link=link))

##### printer #####
t=time.localtime(time.time())
file_printer=time.strftime("/home/gkxk/tmp/printer.txt",t)
year,month,day=time.strftime("%Y",t),time.strftime("%m",t).lstrip('0'),time.strftime("%d",t).lstrip('0')
with open(path_join(md_path,'life.md')) as f:
    text_year=f.read()
    res=re.search('year-{}\) : (.*)\n'.format(year),text_year)
    text_year=res.group(1)
with open(path_join(md_path,file_year)) as f:
    text_month=f.read()
    res=re.search('month-{}-{}\) : (.*)\n'.format(year,month),text_month)
    text_month=res.group(1)
with open(path_join(md_path,file_month)) as f:
    text_day=f.read()
    #res=re.search('day-{}-{}-{}\) : (.*)\n'.format(year,month,day),text_day)
    res=re.search('{}日 : (.*)\n'.format(day),text_day)
    text_day=res.group(1)
# with open(path_join(md_path,file_day)) as f:
#     text_hour=''.join(f.readlines()[2:])
#     text_hour=text_hour.replace('\n','\n    \n')
with open(path_join(md_path,'../todo.md')) as f:
    lines=f.readlines()
    rules=lines[lines.index('### rules\n')+1:]
    rules=rules[:rules.index('\n')]
    tmp=''
    for rule in rules:
        tmp=tmp+rule.replace('- ', '').replace('\n','')+';'
    rules=tmp
with open(file_printer,'w') as f:
    #text='rules : {rules}\n{year}-{month}-{day} : {day_text}\n  \n  \n  \n  \n{hour_text}- \n \n  \n'.format(rules=rules,year=year,month=month,day=day,year_text=text_year,month_text=text_month,day_text=text_day,hour_text=text_hour)
    #text='{year}-{month}-{day} : {day_text}\n\n\n \n\n\n \n'.format(rules=rules,year=year,month=month,day=day,year_text=text_year,month_text=text_month,day_text=text_day,hour_text=text_hour)
    text='{year}-{month}-{day} : {day_text}\n7:00-11:30(4.5h)\n\n\n \n\n\n \n12:00-5:30(5.5h)\n\n\n \n\n\n \n6:00-0:00(6h)\n\n\n \n\n\n \n- \n\n\n \n'.format(year=year,month=month,day=day,day_text=text_day)
    f.write(text)
    print(text)
