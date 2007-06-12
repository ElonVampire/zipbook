import traceback
import urlparse
import sys
import os
from optparse import OptionParser
import time

pwd = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, pwd)
sys.path.insert(0, os.path.dirname(pwd))

from apps.zipbooks.models import Book, Chapter
from plugins import tools
from django.conf import settings

modules = {}

def refresh_book(url, proxy=None):
    try:
        book = Book.objects.get(url=url)
        book.save()
    except Book.DoesNotExist:
        return get_book(url, proxy)
    mod = get_module(book.url)
    s = []
    for o in book.chapter_set.filter(size=0).values('id', 'url', 'name'):
        url = urlparse.urljoin(book.url, o['url'])
            
        s.append((o['id'], o['url'], o['name']))
    try:
        book.status = 1
        book.message = ''
        book.save()
        get_chapters(s, book.id, proxy=proxy)
    finally:
        book.status = 2
        book.finished = book.chapter_set.filter(size__gt=0).count()
        book.save()
        
def get_book(url, proxy=None):
    print 'Grabbing...', url, time.strftime("%H:%M:%S")
    s = tools.get_url(url, proxy)
    if s:
        mod = get_module(url)
        name = mod.parse_title(s)
        try:
            book = Book.objects.get(name=name)
            book.status = 1
            book.url = url
            book.message = ''
            book.save()
            book.chapter_set.all().delete()
        except Book.DoesNotExist:
            book = Book.objects.create(name=name, url=url)
        
        try:
            try:
                parse_index(url, book, s, proxy)
            except Exception, e:
                traceback.print_exc()
                book.message = str(e)
                return False, str(e)
        finally:
            book.status = 2
            book.finished = book.chapter_set.filter(size__gt=0).count()
            book.save()
        print 'successful!', time.strftime("%H:%M:%S")
    else:
        print 'Parsing URL(%s) failed!' % url, time.strftime("%H:%M:%S")
    
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
    from django.db import transaction
    
    mod = get_module(baseurl)
    i = 0
    s = []
    
    try:
        transaction.enter_transaction_management()
        transaction.managed(True)
    
        print 'index', time.strftime("%H:%M:%S")
        for (url, title) in mod.parse_index(text):
            url = urlparse.urljoin(baseurl, url)
            i += 1
            chapter = Chapter.objects.create(name=title, order=i, url=url, book=book)
            s.append((chapter.id, url, title))
            
        transaction.commit() 
    finally:
        transaction.leave_transaction_management()
    
    print 'index end', time.strftime("%H:%M:%S")
    book.count = i
    book.save()
    get_chapters(s, book.id, proxy=proxy)
 
import threading
class Parse(threading.Thread):
    def __init__(self, q, book_id, proxy=None):
        threading.Thread.__init__(self)
        self.q = q
        self.book_id = book_id
        self.proxy = proxy
        self.setDaemon(True)
            
    def run(self):
        while not self.q.empty():
            (id, url, title) = self.q.get()
            parse_page(self.book_id, id, url, title, self.proxy)
            
import Queue
def get_chapters(s, book_id, n=10, proxy=None):
    q = Queue.Queue()
    for v in s:
        q.put(v)
    t = []
    for i in range(n):
        v = Parse(q, book_id, proxy)
        t.append(v)
        v.start()
        
    for i in t:
        i.join()
        
def parse_page(book_id, id, url, title, proxy):
    print 'Getting...', url
    mod = get_module(url)
    chapter = Chapter.objects.get(pk=id)
    text = tools.get_url(url, proxy)
    content = mod.parse_page(title, text)
    if settings.CONTENT == 'db':
        chapter.content = content
    else:
        path = os.path.join(settings.MEDIA_ROOT, 'zipbooks', str(book_id))
        if not os.path.exists(path):
            os.makedirs(path)
        filename = os.path.join(path, "%04d.txt" % chapter.order)
        try:
            f = file(filename, 'wb')
            f.write(content)
            f.close()
        except:
            traceback.print_exc()
            print 'Getting...', url, 'Failed'
            return
    chapter.size = len(content)
    chapter.save()
    print 'Getting...', url, 'Done'
        
def get_usage():
    usage = """
  %prog get url
  %prog reget url
"""
    return usage

def execute_from_command_line(argv=None):
    # Use sys.argv if we've not passed in a custom argv
    if argv is None:
        argv = sys.argv

    # Parse the command-line arguments. optparse handles the dirty work.
    parser = OptionParser(usage=get_usage())
    parser.add_option('--settings',
        help='Python path to settings module, e.g. "myproject.settings.main". If this isn\'t provided, the DJANGO_SETTINGS_MODULE environment variable will be used.')
    parser.add_option('--proxy',
        help='Proxy will be used. Default is using your env settings.')
    parser.add_option('-u', '--proxyuser', help='Proxy user name.')
    parser.add_option('-p', '--proxypassword', help='Proxy password.')

    options, args = parser.parse_args(argv[1:])
    
    if len(args) != 2:
        parser.print_help()
        sys.exit(0)
        
    action = args[0]
    url = args[1]
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    else:
        from django.core.management import setup_environ
        try:
            import settings
        except ImportError:
            print "You don't appear to have a settings file in this directory!"
            print "Please run this from inside a project directory"
            sys.exit()
            
        setup_environ(settings)

    if options.proxy:
        proxy = {'host':options.proxy, 'user':options.proxyuser, 'password':options.proxypassword}
    else:
        proxy = None
    if action == 'get':
        get_book(url, proxy)
    elif action == 'reget':
        refresh_book(url, proxy)
    else:
        parser.print_help()

if __name__ == '__main__':
    execute_from_command_line()
    
