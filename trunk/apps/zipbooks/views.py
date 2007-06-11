# Create your views here.
from utils.common import render_template
from utils.ajax import ajax_ok, ajax_fail
from apps.zipbooks.models import Book
from apps.zipbooks.validator import AddValidator
from getbook import getbook
from django.http import HttpResponse
from utils.lib_page import Page

def index(request):
    return render_template(request, 'zipbooks/index.html')

def add(request):
    v = AddValidator()
    f, obj = v.validate(request)
    if f:
        try:
            f, msg = getbook(v.clean_data()['url'])
        except Exception, e:
            import traceback
            traceback.print_exc()
            return ajax_fail(message=str(e))
        if f:
            return ajax_ok({'id':msg.id}, message='Successful!', next='')
        else:
            return ajax_fail(message=msg)
    return ajax_fail(obj, message="There are something wrong")
        
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
    