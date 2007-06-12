#coding=gb2312
import re
import tools

r_subject = re.compile(r'<TITLE>([^_]+).*?</TITLE>', re.DOTALL)
r_index = re.compile(r'<a href=([^\s]+) target=_blank class=a03>(.*?)</a>', re.DOTALL)
r_meta = re.compile(r'<META http-equiv=content-type content="text/html; charset=(.*?)">', re.DOTALL|re.IGNORECASE)
r_content = re.compile(r'<div class="artibody" id="artibody">(.*?)</div>', re.DOTALL)
r_title = re.compile(r'<TITLE>([^_]+).*?</TITLE>', re.DOTALL)
def parse_title(text, proxy=None):
    r = r_subject.search(text)
    if r:
        subject = r.group(1)
#        subject = subject.split('_', 1)[0]
    else:
        subject = 'unknow'
    return tools.to_utf8(subject)
    
def parse_index(text, proxy=None):
#    r = r_meta.search(text)
#    if r:
#        encoding=r.group(1)
#        if encoding.lower() == 'gb2312':
#            encoding = 'gb18030'
#    else:
#        encoding='gb18030'
    s = []
    for (url, title) in r_index.findall(text):
        title = title.replace('&nbsp;', ' ')
        yield url, tools.to_utf8(title)
        
def parse_page(title, text, proxy=None):
#    r = r_meta.search(text)
#    if r:
#        encoding=r.group(1)
#        if encoding.lower() == 'gb2312':
#            encoding = 'gb18030'
#    else:
#        encoding='gb18030'
    r = r_title.search(text)
    if r:
        title = r.group(1).strip()
        title = tools.to_utf8(title)
        
    r = r_content.search(text)
    if r:
        text = tools.format_html_text(r.group(1))
    else:
        text = ''
    return title + '\r\n'*2 + text

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
