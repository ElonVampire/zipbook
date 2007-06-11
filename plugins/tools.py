import re

def to_utf8(text, encoding='gb18030'):
    return unicode(text, encoding, 'ignore').encode('utf-8')

def to_encode(text, encoding='gb18030'):
    return unicode(text, 'utf-8').encode(encoding, 'ignore')
    
def format_html_text(text):
    text = text.strip().replace('&nbsp;', ' ')
    text = re.sub(r'\n|\r', '', text)
    text = re.sub(r'(?i)<p>', '\r\n\r\n', text)
    text = re.sub(r'(?i)<br.*?>', '\r\n', text)
    b = re.compile(r'<.*?>', re.DOTALL)
    text = b.sub('', text)
    
    def s(m):
        if m.group(1):
            return unichr(int(m.group(1))).encode('utf-8')
        return m.group()
    text = to_utf8(text)
    text = re.sub(r'&#(\d+);', s, text)
    return text
    