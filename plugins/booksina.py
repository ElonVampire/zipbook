#coding=gb2312
import re

r_subject = re.compile(r'<TITLE>([^_]+).*?</TITLE>', re.DOTALL)
r_index = re.compile(r'<a href=([^\s]+) target=_blank class=a03>(.*?)</a>', re.DOTALL)
r_meta = re.compile(r'<META http-equiv=content-type content="text/html; charset=(.*?)">', re.DOTALL|re.IGNORECASE)
r_content = re.compile(r'<div class="artibody" id="artibody">(.*?)</div>', re.DOTALL)
r_title = re.compile(r'<TITLE>([^_]+).*?</TITLE>', re.DOTALL)
def parse_title(text):
    r = r_subject.search(text)
    if r:
        subject = r.group(1)
#        subject = subject.split('_', 1)[0]
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
        text = r.group(1).strip().replace('&nbsp;', ' ').replace('</p>', '')
        text = re.sub(r'\n|\r', '', text)
        text = re.sub(r'<p>', '\r\n\r\n', text)
        b = re.compile(r'<.*?>', re.DOTALL)
        text = b.sub('', text)
    else:
        text = ''
    return title + '\r\n'*2 + unicode(text, encoding, errors='ignore').encode('utf-8')

if __name__ == '__main__':
    text = file('sina_a.html').read()
    print 'title=', unicode(parse_title(text), 'utf-8', errors='ignore').encode('gb18030')
    print 'index='
    i = 0
    for url, title in parse_index(text):
        print unicode(title, 'utf-8', errors='ignore').encode('gb18030'), url
        i += 1
    print 'total=', i
    print 'page='
    print unicode(parse_page('title', file('sina_b.html').read()), 'utf-8', errors='ignore').encode('gb18030', 'ignore')
