import urllib
import traceback
from apps.zipbooks.models import Book, Chapter
import urlparse

modules = {}

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

def continue_book(book_id, proxy=None):
    book = Book.objects.get(pk=int(book_id))
    mod = get_module(book.url)
    s = []
    for o in book.chapter_set.filter(status__in=(0, 1)).values('id', 'url', 'name'):
        url = urlparse.urljoin(book.url, o['url'])
            
        s.append((o['id'], o['url'], o['name']))
    get_chapters(s, proxy=proxy)
    
def getbook(url, proxy=None):
    s = _get_page(url, proxy)
    if s:
        mod = get_module(url)
        name = mod.parse_title(s)
        try:
            book = Book.objects.get(name=name)
            book.count = 0
            book.finished = 0
            book.save()
        except Book.DoesNotExist:
            book = Book.objects.create(name=name, url=url)
        
        try:
            parse_index(url, book, s, proxy)
        except Exception, e:
            import traceback
            traceback.print_exc()
            return False, str(e)
        return True, book
    else:
        return False, 'Parsing URL(%s) failed!' % url
    
def get_module(url):
    domain = urlparse.urlparse(url)[1]
    if domain in modules:
        return modules[domain]
    else:
        import plugins
        modname = plugins.get_mod(domain)
        if not modname:
            raise Exception, 'There is no support for %s site.' % domain 
        mod = __import__('plugins.%s' % modname, {}, {}, [''])
        modules[domain] = mod
        return mod
    
def parse_index(baseurl, book, text, proxy):
    mod = get_module(baseurl)
    i = 0
    s = []
    for (url, title) in mod.parse_index(text):
        url = urlparse.urljoin(baseurl, url)
        i += 1
        try:
            chapter = Chapter.objects.get(name=title, book=book)
            chapter.order = i
            chapter.url = url
            chapter.status = 0
            chapter.save()
        except Chapter.DoesNotExist:
            chapter = Chapter.objects.create(name=title, order=i, url=url, book=book)
            
        s.append((chapter.id, url, title))
    book.count = i
    book.save()
    get_chapters(s, proxy=proxy)
 
import threading
class Parse(threading.Thread):
    def __init__(self, q, proxy=None):
        threading.Thread.__init__(self)
        self.q = q
        self.proxy = proxy
        self.setDaemon(True)
            
    def run(self):
        while not self.q.empty():
            (id, url, title) = self.q.get()
            parse_page(id, url, title, self.proxy)
            
import Queue
def get_chapters(s, n=10, proxy=None):
    q = Queue.Queue()
    for v in s:
        q.put(v)
    t = []
    for i in range(n):
        v = Parse(q, proxy)
        t.append(v)
        v.start()
        
    for i in t:
        i.join()
        
def parse_page(id, url, title, proxy):
    mod = get_module(url)
    chapter = Chapter.objects.get(pk=id)
    chapter.status = 1
    chapter.save()
    text = _get_page(url, proxy)
    content = mod.parse_page(title, text)
    chapter.content = content
    chapter.size = len(content)
    chapter.status = 2
    chapter.save()
        
if __name__ == '__main__':
    getbook('http://www.duyidu.com/Article/xhxs/ksxh/Index.asp')