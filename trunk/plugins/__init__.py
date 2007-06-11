#coding=gb2312
modname = {
    'www.duyidu.com':('duyidu', '读一读', 'http://www.duyidu.com'),
    'www.readnovel.com':('readnovel', '小说阅读网', 'http://www.readnovel.com'),
    'book.sina.com.cn':('booksina', '新浪读书', 'http://book.sina.com.cn'),
}
def get_mod(domain):
    return modname.get(domain, (None, None, None))[0]

