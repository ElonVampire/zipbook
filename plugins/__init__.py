#coding=utf-8
modname = {
    'duyidu.com':('duyidu', '读一读', 'http://www.duyidu.com'),
    'readnovel.com':('readnovel', '小说阅读网', 'http://www.readnovel.com'),
    'book.sina.com.cn':('booksina', '新浪读书', 'http://book.sina.com.cn'),
    'cmfu.com':('cmfu', '起点中文网', 'http://www.cmfu.com'),
    '17k.com':('17k', '17K文学网', 'http://www.17k.com'),
    'book.qq.com':('bookqq', '腾讯读书网', 'http://book.qq.com/'),
    'cul.news.tom.com':('cultom', 'TOM书吧', 'http://cul.news.tom.com/'),
    'read.2100book.com':('2100book', '世纪文学', 'http://read.2100book.com/'),
}
def get_mod(domain):
    return modname.get(domain, (None, None, None))[0]

def show_sites(n):
    s = ['<table border=0>']
    i = 0
    for k, v in modname.items():
        _, title, url = v
        if i % n == 0:
            if i != 0:
                s.append('</tr>')
            s.append('<tr>')
        s.append('<td><a href="%s"><img src="/site_media/img/site.gif"/> %s</a></td>' % (url, title))
        i += 1
    if i>0:
        s.append('</tr>')
    s.append('</table>')
    return ''.join(s)
    
if __name__ == '__main__':
    print show_sites(3)
        