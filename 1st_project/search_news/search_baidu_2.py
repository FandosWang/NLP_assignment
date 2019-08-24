#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 主任务：利用爬虫收集新闻信息，进行人物观点分析
# 本脚本任务：爬取信息并保存到数据库中
import re
import pickle
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib import request
import chardet
from urllib import parse

# 利用百度搜索引擎按关键词搜索热点新闻
keyword = input("请输入关键词(如：成龙)：")
url_baidu = "http://www.baidu.com/s?tn=news&word=" + keyword
print(url_baidu)
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

# 定义函数用于提取百度搜索页面的新闻网址和下一页网址

def get_url(url):
    
     # 提取搜索页面网址    
    search_result = requests.get(url, headers=headers).text
    search_result = search_result.replace("\n","")   # 删除换行符，因为换行符不好匹配

    # 首先定位搜索结果所在的区间，避免引入大量垃圾网址
    results_re = r'<div class="result" id="\d+">(.*)</div>'
    results = re.compile(results_re).findall(search_result)

    # 在区间内搜索网址
    url_news_re = r'<a href="(https?://\S*)"'
    url_news = re.compile(url_news_re).findall(str(results))
    #print(url_news)
    
    # 提取百度下一页按钮网址
    url_next_page_re = '<a href="(\S*)"\ class="n">下一页&gt;</a>'
    url_next_page_0 = re.compile(url_next_page_re).findall(str(results))
    url_next_page = 'http://www.baidu.com' + url_next_page_0[0]
    print(url_next_page)
    
    return url_news, url_next_page

# 打开搜索结果中的网址，爬取新闻信息

def extract_text_by_bs(doc_text):
    """提取html页面的所有文本信息。 """
    title, text = '', ''
    soup = BeautifulSoup(doc_text, 'lxml')    # lxml, html5lib
    
    
    try:
        for script in soup(["script", "style"]):
            script.extract()
    except Exception as error:
        print('error')
        pass
    else:
        try:
            # get text
            title = soup.title.string
        except Exception as error:
            print('error')
            pass
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
    return text


# 设置访问页数
max_number_of_page = 10000

# 用于保存每个网页的新闻信息
news = []

for page_number in range(max_number_of_page):
    
    # 第一次，给定地址,第二次以后，都用下一页地址
    if page_number == 0:
        url_news, url_next_page = get_url(url_baidu)
    else:
        url_news, url_next_page = get_url(url_next_page)

    # 开始遍历url_news中的每个网址，提取网页内容 
    for url in url_news:
        
        # 临时网址无效，不需要登录
        if 'cache' in url:
            continue

        try:
            # 提取网页信息，并判断其编码方式
            news_page = requests.get(url, headers=headers)

        except:
            print('网址打不开！')
            continue
            # 登录不上的网址，不继续进行解析
        if "503 Service Temporarily Unavailable" in news_page.text:
                continue

        try:
            # 如果不知道是什么编码，则放弃这条新闻，不是好办法，先凑合着用
            response = request.urlopen(url)
            charset = chardet.detect(response.read())     #对该html进行编码的获取
            coding_style = charset['encoding']
            # 如果不是utf_8编码，则放弃这条新闻，不是好办法，先凑合着用
            if coding_style != 'utf-8':
                print(f'编码为{coding_style},不是utf-8编码，暂时放弃收录！', end=' ')
                continue
        except:
            print('解码错误！', end=' ')
            continue
         
        try:
            news_page.encoding = "utf-8"
            text = extract_text_by_bs(news_page.text)
        except:
            text = []
            
        if text is not []:
            #print(text[:100])
            news.append(text)
            print(len(news), end=' ')

# 将新闻信息保存到文件中
pickle.dump(news, open("news.pkl","wb"))
# 转化成Series，作为对比
news_series = pd.Serise(news)
pickle.dump(news_series, open("news_series.pkl","wb"))
# 随机查看文本
#print(news[300:320])

