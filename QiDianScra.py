#! /bin/python3
#coding=utf-8
"""
说明：1、运行前安装好相应的库
     2、linux下脚本运行方式，终端键入如下命令：
       >sudo chmod u+x QiDianScra.py
       >./QiDianScra.py
     3、windows下运行方式：
        a、删除此文件的首行，即(#! /bin/python)
        b、在文件目录下启动cmd
        c、命令提示符下键入python QiDianScra.py
        d、输出结果在out.csv中
"""
import requests,json,time,re
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
from fontTools.ttLib import TTFont
from io import BytesIO
import pandas as pd

start_url = 'https://www.qidian.com/finish?action=hidden&orderId=3&vip=1&sign=1&style=2&pageSize=50&siteid=1&pubflag=0&hiddenField=2&page='

def get_font(url):
    response = requests.get(url)
    font = TTFont(BytesIO(response.content))
    cmap = font.getBestCmap()
    font.close()
    return cmap

def get_encode(cmap,values):
    WORD_MAP = {'zero':'0','one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','period':'.'}
    word_count=''
    for value in values.split(';'):
        value = value[2:]
        key = cmap[int(value)]
        word_count += WORD_MAP[key]
    return word_count

def get_index(start_url):
    #获取当前页面的html
    response = requests.get(start_url).text   
    doc = pq(response)
    #获取当前字体文件名称（point1）
    classattr = doc('tr .total span').attr('class')
    pattern = '</style><span.*?%s.*?>(.*?)</span>'%classattr
    #获取当前页面所有被字数字符
    numberlist = re.findall(pattern,response)
    #获取当前包含字体文件链接的文本（point2）
    fonturl = doc('tr .total style').text() 
    #通过正则获取当前页面字体文件链接
    url = re.search('woff.*?url.*?\'(.+?)\'.*?truetype',fonturl) .group(1)
    cmap = get_font(url)
    #point3
    books = doc('tbody > tr').items()
    i = 0
    df = pd.DataFrame()
    for book in books:
        item = {}
        item['类别'] = book('.td-one').text()
        item['小说名称'] = book('.name').text()
        item['最新章节'] = book('.chapter').text()
        item['字数'] = get_encode(cmap,numberlist[i][:-1])
        item['作者'] = book('.author').text()        
        item['更新时间'] = book('.date').text()
        i += 1
        df = df.append(item, ignore_index=True)
    return df

def main():
    df = pd.DataFrame()
    for page in range(1,197):
        url = start_url + str(page)
        df = df.append(get_index(url))
    df.to_csv('out.csv')


if __name__ == '__main__':
    main()
