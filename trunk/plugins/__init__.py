#coding=gb2312
modname = {
    'www.duyidu.com':('duyidu', '��һ��', 'http://www.duyidu.com'),
    'www.readnovel.com':('readnovel', 'С˵�Ķ���', 'http://www.readnovel.com'),
    'book.sina.com.cn':('booksina', '���˶���', 'http://book.sina.com.cn'),
}
def get_mod(domain):
    return modname.get(domain, (None, None, None))[0]

