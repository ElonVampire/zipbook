#coding=gb2312
import re
import tools

r_subject = re.compile(r'<h1 .*?>(.*?)</h1>', re.DOTALL)
r_index = re.compile(r"<a href='javascript:gotopage\((.*?)\)[^>]*>(.*?)</a>", re.DOTALL)
r_meta = re.compile(r'<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=(.*?)">', re.DOTALL|re.IGNORECASE)
r_content = re.compile(r"<script src='(.*?\.txt)'></script>", re.DOTALL)
r_title = re.compile(r'<title>(.*?)</title>', re.DOTALL)
r_bookid = re.compile(r'function gotopage.*?&bl_id=(\d+)', re.DOTALL)

def parse_title(text):
    r = r_subject.search(text)
    if r:
        subject = r.group(1)
    else:
        subject = 'unknow'
    return tools.to_utf8(subject)
    
def parse_index(text):
#    r = r_meta.search(text)
#    if r:
#        encoding=r.group(1)
#        if encoding.lower() == 'gb2312':
#            encoding = 'gb18030'
#    else:
#        encoding='gb18030'
    r = r_bookid.search(text)
    if r:
        id = r.group(1)
    else:
        raise Exception, "can't find the book id"
    s = []
    for (c_id, title) in r_index.findall(text):
        url = "readchapter.asp?bu_id=" + c_id + "&bl_id=" + id
        title = title.replace('&nbsp;', ' ')
        yield url, tools.to_utf8(title)
        
def parse_page(title, text):
#    r = r_meta.search(text)
#    if r:
#        encoding=r.group(1)
#        if encoding.lower() == 'gb2312':
#            encoding = 'gb18030'
#    else:
#        encoding='gb18030'
    r = r_title.search(text)
    if r:
        title = r.group(1).strip().split('/')[1]
        title = tools.to_utf8(title)
        
    r = r_content.search(text)
    if r:
        url = r.group(1)
        text = _get_page(url).strip()
        b = "document.write('"
        e = "');"
        if text.startswith(b) and text.endswith(e):
            text = text[len(b):-1*len(e)]
        text = tools.format_html_text(text)
    else:
        text = ''
    return title + '\r\n'*2 + text

import traceback
import urllib
def _get_page(url, proxy=None):
    s = []
    for i in range(3):
        try:
            f = urllib.urlopen(url, proxies=proxy)
            print url
            while 1:
                text = f.read(1024)
                if not text:
                    break
                print '.',
                s.append(text)
        except:
            traceback.print_exc()
            pass
        else:
            break
    return ''.join(s)

if __name__ == '__main__':
    text = file('cmfu_a.html').read()
    print 'title=', tools.to_encode(parse_title(text))
    print 'index='
    i = 0
    for url, title in parse_index(text):
        print tools.to_encode(title), url
        i += 1
    print 'total=', i
    print 'page='
    print tools.to_encode(parse_page('title', file('cmfu_b.html').read()))
