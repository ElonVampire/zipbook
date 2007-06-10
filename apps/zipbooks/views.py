# Create your views here.
from utils.common import render_template
from utils.ajax import ajax_ok, ajax_fail
from apps.zipbooks.models import Book
from apps.zipbooks.validator import AddValidator
from getbook import getbook
from django.http import HttpResponse

def index(request):
    return render_template(request, 'zipbooks/index.html')

def add(request):
    v = AddValidator()
    f, obj = v.validate(request)
    if f:
        try:
            f, msg = getbook(v.clean_data()['url'])
        except:
            import traceback
            traceback.print_exc()
            return ajax_fail(message='error')
        if f:
            return ajax_ok({'id':msg.id}, message='Successful!', next='')
        else:
            return ajax_fail(message=msg)
    return ajax_fail(obj, message="There are something wrong")
        
def booklist(request):
    s = []
    for o in Book.objects.all():
        s.append({'id':o.id, 'title':o.name, 'url':o.url, 'finished':'%d%%' % (o.finished*100/o.count)})
    return ajax_ok(s)

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
        f.addstring(book.name + '.txt', '\r\n\r\n'.join(c))
    else:
        for o in book.chapter_set.all():
            f.addstring(("%04d" % o.order)+'.txt', o.content)
    f.close()
    
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % book.name
    
    response.write(file(filename, 'rb').read())
    return response
    