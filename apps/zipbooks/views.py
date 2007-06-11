#coding=utf-8
# Create your views here.
from utils.common import render_template
from utils.ajax import ajax_ok, ajax_fail
from apps.zipbooks.models import Book
from getbook import getbook
from django.http import HttpResponse
from utils.lib_page import Page

def index(request):
    return render_template(request, 'zipbooks/index.html')

def add(request):
    url = request.POST.get('url', '')
    if url:
        try:
            f, msg = getbook(url)
        except Exception, e:
            import traceback
            traceback.print_exc()
            return ajax_fail(message=str(e))
        if f:
            return ajax_ok({'id':msg.id}, message='处理成功')
        else:
            return ajax_fail(message=msg)
    return ajax_fail(message="请输入想下载书的目录URL")
        
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
            c.append(o.content)
        f.addstring(unicode(book.name, 'utf-8').encode('gb18030', 'ignore') + '.txt', '\r\n\r\n'.join(c))
    else:
        for o in book.chapter_set.all():
            f.addstring(("%04d" % o.order)+'.txt', o.content)
    f.close()
    
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % book.name
    
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
                
        