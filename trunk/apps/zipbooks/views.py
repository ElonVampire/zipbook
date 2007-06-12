#coding=utf-8
# Create your views here.
from utils.common import render_template
from utils.ajax import ajax_ok, ajax_fail
from apps.zipbooks.models import Book
from django.http import HttpResponse
from utils.lib_page import Page
from django.conf import settings
import os, sys
import traceback
from plugins import tools

def index(request):
    return render_template(request, 'zipbooks/index.html')

def add(request, book_id=None):
    if book_id:
        try:
            book = Book.objects.get(pk=int(book_id))
        except Book.DoesNotExist:
            return ajax_fail(message="此书在数据库中不存在！")
        url = book.url
    else:
        url = request.POST.get('url', '')
    if url:
        args = list(settings.PARAMS) + ['get', url]
        try:
           os.spawnl(*args)
        except:
            traceback.print_exc()
        return ajax_ok(message="任务已经提交！请稍候下载。")
    return ajax_fail(message="请输入想下载书的目录URL")

def refresh(request, book_id):
    try:
        book = Book.objects.get(pk=int(book_id))
    except Book.DoesNotExist:
        return ajax_fail(message="此书在数据库中不存在！")
    args = list(settings.PARAMS) + ['reget', book.url]
    try:
       os.spawnl(*args)
    except:
        traceback.print_exc()
    return ajax_ok(message="任务已经提交！请稍候下载。")
        
def booklist(request):
    s = []
    pagenum = 60
    objs = Book.objects.all()
    page = Page(objs, request, paginate_by=pagenum)
    for o in page.object_list:
        s.append({'id':o.id, 'title':o.name, 'url':o.url, 'finished':o.finished*100/o.count})
    pages = (objs.count() + pagenum - 1) / pagenum
    cur = int(request.GET.get('page', 1))
    return ajax_ok((cur, pages, s))

def _get_content(book_id, path, o):
    if settings.CONTENT == 'db':
        return o.content
    else:
        filename = os.path.join(path, str(book_id), "%04d.txt" % o.order)
        if os.path.exists(filename):
            try:
                f = file(filename, 'rb')
                text = f.read()
                f.close()
                return text
            except:
                traceback.print_exc()
        return ''
    
def download(request, book_id):
    from utils.zfile import ZFile
    import os
    from django.conf import settings
    
    book = Book.objects.get(pk=int(book_id))
    path = os.path.join(settings.MEDIA_ROOT, 'zipbooks')
    if not os.path.exists(path):
        os.makedirs(path)
    filename = os.path.join(path, str(book.id) + '.zip')
    f = ZFile(filename, 'w')
    if request.GET.get('onefile', ''):
        c = []
        for o in book.chapter_set.all():
            c.append(_get_content(book.id, path, o))
        f.addstring(tools.to_encode(book.name) + '.txt', '\r\n\r\n'.join(c))
    else:
        for o in book.chapter_set.all():
            f.addstring(("%04d" % o.order)+'.txt', _get_content(book.id, path, o))
                
    f.close()
    
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % tools.to_encode(book.name)
    
    response.write(file(filename, 'rb').read())
    return response
    
def search(request):
    word = request.POST.get('search', '')
    s = []
    if word:
        objs = Book.objects.filter(name__icontains=word)
    else:
        objs = Book.objects.all()
    for o in objs:
        s.append({'id':o.id, 'title':o.name, 'url':o.url, 'finished':o.finished*100/o.count})
    return ajax_ok(s)
                
def monitor(request):
    s = []
    objs = Book.objects.filter(status__in=(0, 1))
    for o in objs:
        s.append({'id':o.id, 'title':o.name, 'url':o.url, 'finished':o.finished*100/o.count, 'status':o.status})
    return ajax_ok(s)
    