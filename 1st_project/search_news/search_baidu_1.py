# 主任务：利用爬虫收集新闻信息，进行人物观点分析
# 本脚本任务：爬取信息并保存到数据库中
import re

import pandas
import requests
from bs4 import BeautifulSoup

# 利用百度搜索引擎按关键词搜索热点新闻
#keyword = input("请输入关键词：")
keyword = "李现"
url_baidu = "http://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word=" + keyword
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
search_result = requests.get(url_baidu, headers=headers).text
search_result = search_result.replace("\n","")   # 删除换行符，因为换行符不好匹配


# 爬取搜索结果的网址
# 首先定位搜索结果所在的区间，避免引入大量垃圾网址
results_re = r'<div class="result" id="\d+">(.*)</div>'
results = re.compile(results_re).findall(search_result)
# 在区间内搜索网址

url_news_re = r'<a href="(https?://\S*)"'
url_news = re.compile(url_news_re).findall(str(results))


# 打开搜索结果中的网址，爬取新闻信息
def extract_text_by_bs(doc_text):
    """提取html页面的所有文本信息。 """
    title, text = '', ''
    soup = BeautifulSoup(doc_text, 'lxml')
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
    return title, text


news = []
for url in url_news:
    # 临时网址无效，不需要登录
    if 'cache' in url:
        continue
    news_page = requests.get(url, headers=headers).text
    #news_page = news_page.replace("\n", "")  # 删除换行符，因为换行符不好匹配

    # 登录不上的网址，不继续进行解析
    if "503 Service Temporarily Unavailable" in news_page:
        continue
    title, text = extract_text_by_bs(news_page)
    news.append(text)

print(news)
# 简单处理新闻信息

# 将新闻信息保存到数据库中