import requests
from bs4  import BeautifulSoup
url = 'https://baijiahao.baidu.com/s?id=1601513200373576360&wfr=spider&for=pc'
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
page = requests.get(url, headers=headers).text


def extract_text_by_bs(doc_text):
    """提取html页面的所有文本信息。
    参考：
    http://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    """
    title, text = '', ''
    soup = BeautifulSoup(doc_text, 'lxml')
    try:
        for script in soup(["script", "style"]):
            script.extract()
    except Exception as error:
        print ('error')
        pass
    else:
        try:
            # get text
            title = soup.title.string
        except Exception as error:
            print ('error')
            pass
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
    return title, text

title, text = extract_text_by_bs(page)

print(title)
print(text)
