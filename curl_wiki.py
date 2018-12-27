# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 16:01:04 2016

@author: liuhaitao@live.cn
"""
import re
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import requests
from langconv import *
from operator import itemgetter
import numpy as np

# proxies = {
#         'http': 'http://127.0.0.1:8087',
#         'https': 'http://127.0.0.1:8087',
# }
url = "https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E8%BF%90%E8%BD%BD%E7%81%AB%E7%AE%AD%E5%8F%91%E5%B0%84%E5%88%97%E8%A1%A8"

s = requests.Session()
# rsp = s.get(url, proxies=proxies, verify=False)
rsp = s.get(url, )
data = rsp.text
rsp.close()
loc = {'酒泉': [40.96069, 100.29818],
       '西昌': [28.24703, 102.02905],
       '太原': [38.8632, 111.5896],
       '文昌': [19.6146, 110.95111]}


# return
# print(data)

def bs_format(data):
    #    data=opencc.convert(data)
    soup = BeautifulSoup(data, 'lxml')
    id_re = re.compile('(?P<num>\d+)\.')
    tmpRecord = []

    for table in soup.find_all('table'):
        tmp = table.find('tr').find('th')
        if tmp is not None:
            print(tmp.get_text())
            if Converter('zh-hans').convert(tmp.get_text()).strip() \
                    != '中国运载火箭发射列表':
                #            print('no')
                continue
        #            else:
        #            print('yes')
        else:
            continue
        for tr in table.find_all('tr'):
            tmp = tr.find('td')
            if tmp is not None:
                tmp = re.match('(?P<id>\d+\.)', tmp.get_text())
                if tmp:
                    #                    print(tmp.group())
                    pass
                else:
                    continue
                tmp = tr.find_all('td')
                tmprecord = []
                for i in range(len(tmp)):
                    tmprecord.append(Converter('zh-hans').convert(tmp[i].get_text()))
                tmpRecord.append(tmprecord)
    #            for td in tr.find_all('td'):
    #                print(td.get_text())
    record = []
    toUTC = pd.Timedelta(hours=-8)
    for tmpItem in tmpRecord:
        item = [None] * 13
        item[0] = int(id_re.search(tmpItem[0]).group('num'))
        if tmpItem[6][0] != '1':
            item[1] = 0
        else:
            item[1] = 1
        print(tmpItem[3])
        date_str = tmpItem[3][:-1].replace('年', '-').replace('月', '-').replace('日', ' '). \
            replace('\n', ' ').replace('时', ':').replace('点', ':').replace('分', ':').replace('秒', '').strip()
        if date_str[-1] == ':':
            date_str = date_str[:-1]
        item[2 + 2] = pd.Timestamp(date_str) + toUTC
        item[2] = item[4].year
        item[3] = item[4].dayofyear
        item[3 + 2] = tmpItem[1].replace('\n', '').replace(' ', '')
        try:
            this_pos_list = tmpItem[5].replace(';', ' ').strip().split()
            if len(this_pos_list) != 1:
                tmpPot = itemgetter(0, -2, -1)(this_pos_list)
            else:
                tmpPot = [this_pos_list[0], *loc[this_pos_list[0][:2]]]
        except:
            continue
            pass

        item[4 + 2] = tmpPot[0]
        item[5 + 2] = float(tmpPot[1])
        item[6 + 2] = float(tmpPot[2])
        item[7 + 2] = tmpItem[4].split('[')[0].strip()
        print(item[7 + 2])
        item[8 + 2] = tmpItem[2].replace('\n', ' ')
        record.append(item)

    record = pd.DataFrame(record, columns=['series_num', 'status', 'year', 'doy', 'datetime', \
                                           'rocket', 'pot_name', 'pot_lat', 'pot_lon', 'orbit', 'mass', 'dst_mean',
                                           'dst'])
    record = record.set_index('series_num')
    return record


print(data)
record = bs_format(data)
record.to_csv('RocketList.txt')
