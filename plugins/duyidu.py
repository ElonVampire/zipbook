#coding=gb2312
import re
import tools

r_subject = re.compile(r'<title>(.*?)</title>', re.DOTALL)
r_index = re.compile(r'<a\s+class="listA"\s+href="(.*?)"\s+title="(.*?)"', re.DOTALL)
r_meta = re.compile(r'<meta http-equiv="Content-Type" content="text/html; charset=(.*?)">', re.DOTALL)
r_content = re.compile(r'<div id=content>(.*?)</div>', re.DOTALL)
r_title = re.compile(r'<div id=title>(.*?)</div>', re.DOTALL)
def parse_title(text, proxy=None):
    r = r_subject.search(text)
    if r:
        subject = r.group(1)
        subject = subject[:len(subject)-27]
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
        title = r.group(1)
        title = tools.to_utf8(title)
        
    r = r_content.search(text)
    if r:
        text = tools.format_html_text(r.group(1))
    else:
        text = ''
    return title + '\r\n'*2 + text

if __name__ == '__main__':
    text = file('duyidu_a.html').read()
    print 'title=', tools.to_encode(parse_title(text))
    print 'index='
    i = 0
    for url, title in parse_index(text):
        print tools.to_encode(title), url
        i += 1
    print 'total=', i
    print 'page='
    print tools.to_encode(parse_page('title', file('duyidu_b.html').read()))
