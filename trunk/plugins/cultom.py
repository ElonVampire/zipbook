#coding=gb2312
import re
import tools

r_subject = re.compile(r'<title>(.*?)</title>', re.DOTALL)
r_index = re.compile(r'<A title=编辑\s+href="(/.*?)".*?>(.*?)</A>', re.DOTALL|re.IGNORECASE)
r_meta = re.compile(r'<meta http-equiv="Content-Type" content="text/html; charset=(.*?)">', re.DOTALL|re.IGNORECASE)
r_content = re.compile(r'<!--content-->(.*?)<!--content-->', re.DOTALL)
r_title = re.compile(r'<title>(.*?)</title>', re.DOTALL)

def parse_title(text, proxy=None):
    encoding = tools.get_encoding(r_meta, text)
    r = r_subject.search(text)
    if r:
        subject = r.group(1)
        subject = subject.split('_', 1)[0]
    else:
        subject = 'unknow'
    return tools.to_utf8(subject, encoding)
    
def parse_index(text, proxy=None):
    encoding = tools.get_encoding(r_meta, text)
    s = []
    for (url, title) in r_index.findall(text):
        title = title.replace('&nbsp;', ' ').strip()
        yield url, tools.to_utf8(title, encoding)
        
def parse_page(title, text, proxy=None):
    encoding = tools.get_encoding(r_meta, text)
    r = r_title.search(text)
    if r:
        title = r.group(1).split('_', 1)[0]
        title = tools.to_utf8(title, encoding)
        
    r = r_content.search(text)
    if r:
        text = tools.format_html_text(r.group(1), encoding)
    else:
        text = ''
    return title + '\r\n'*2 + text

if __name__ == '__main__':
    text = file('cultom_a.html', 'rb').read()
    print 'title=', tools.to_encode(parse_title(text))
    print 'index='
    i = 0
    for url, title in parse_index(text):
        print tools.to_encode(title), url
        i += 1
    print 'total=', i
    print 'page='
    print tools.to_encode(parse_page('title', file('cultom_b.html').read()))
