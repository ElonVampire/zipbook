import re
import pycurl
import urllib

def get_encoding(r, text):
    b = r.search(text)
    if b:
        encoding=b.group(1)
        if encoding.lower() == 'gb2312':
            encoding = 'gb18030'
    else:
        encoding='gb18030'
    return encoding

def get_url(url, proxy=None):
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    import StringIO
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 300)
    if not proxy:
        proxy_host = urllib.getproxies().get('http', '')
        if proxy_host:
            proxy = {'host':proxy_host}
    if proxy:
        c.setopt(pycurl.PROXY, proxy['host'])
        if proxy.get('user', ''):
            c.setopt(pycurl.PROXYUSERPWD, '%s:%s' % (proxy['user'], proxy['password']))
    c.perform()
    return b.getvalue()

def to_utf8(text, encoding='gb18030'):
    encoding = encoding.lower()
    if encoding in ('utf-8', 'utf8'):
        return text
    if not isinstance(text, unicode):
        text = unicode(text, encoding, 'ignore')
    return text.encode('utf-8')

def to_encode(text, encoding='gb18030'):
    encoding = encoding.lower()
    if encoding in ('utf-8', 'utf8'):
        return text
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8')
    return text.encode(encoding, 'ignore')
    
def format_html_text(text, encoding='gb18030'):
    text = text.strip().replace('&nbsp;', ' ')
    text = re.sub(r'\n|\r', '', text)
    text = re.sub(r'(?i)<p.*?>', '\r\n\r\n', text)
    text = re.sub(r'(?i)<br.*?>', '\r\n', text)
    b = re.compile(r'<.*?>', re.DOTALL)
    text = b.sub('', text)
    
    def s(m):
        if m.group(1):
            return unichr(int(m.group(1))).encode('utf-8')
        return m.group()
    text = to_utf8(text, encoding)
    text = re.sub(r'&#(\d+);', s, text)
    return text
    
if __name__ == '__main__':
    print get_url('http://www.sina.com/')