#coding=gb2312
import re

r_subject = re.compile(r'<title>(.*?)</title>', re.DOTALL)
r_index = re.compile(r'<LI class=bookblog><a href="(.*?)">(.*?)</a>', re.DOTALL)
r_meta = re.compile(r'<meta http-equiv="Content-Type" content="text/html; charset=(.*?)">', re.DOTALL)
r_content = re.compile(r'<div class="content">(.*?)</div>', re.DOTALL)
r_title = re.compile(r'<div class="subhead"><a[^>]+>(.*?)</a></div>', re.DOTALL)
def parse_title(text):
    r = r_subject.search(text)
    if r:
        subject = r.group(1)
        subject = subject[7:len(subject)-2]
    else:
        subject = 'unknow'
    return unicode(subject, 'gb18030', errors='ignore').encode('utf-8')
    
def parse_index(text):
    r = r_meta.search(text)
    if r:
        encoding=r.group(1)
        if encoding.lower() == 'gb2312':
            encoding = 'gb18030'
    else:
        encoding='gb18030'
    s = []
    for (url, title) in r_index.findall(text):
        title = title.replace('&nbsp;', ' ')
        yield url, unicode(title, encoding, errors='ignore').encode('utf-8')
        
def parse_page(title, text):
    r = r_meta.search(text)
    if r:
        encoding=r.group(1)
        if encoding.lower() == 'gb2312':
            encoding = 'gb18030'
    else:
        encoding='gb18030'
    r = r_title.search(text)
    if r:
        title = r.group(1).strip()
        title = unicode(title, encoding, errors='ignore').encode('utf-8')
        
    r = r_content.search(text)
    if r:
        text = r.group(1).strip().replace('&nbsp;', ' ').replace('</P>', '')
        text = re.sub(r'\n|\r', '', text)
        text = re.sub(r'<P>', '\r\n\r\n', text)
    else:
        text = ''
    return title + '\r\n'*2 + unicode(text, encoding, errors='ignore').encode('utf-8')

if __name__ == '__main__':
    text = file('a.html').read()
    print unicode(parse_title(text), 'utf-8', errors='ignore').encode('gb18030')
    i = 0
    for url, title in parse_index(text):
        print unicode(title, 'utf-8', errors='ignore').encode('gb18030'), url
        i += 1
    print 'total', i
    print unicode(parse_page('title', file('b.html').read()), 'utf-8', errors='ignore').encode('gb18030')
