import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

app_dirs = []
for app in settings.INSTALLED_APPS:
    i = app.rfind('.')
    if i == -1:
        m, a = app, None
    else:
        m, a = app[:i], app[i+1:]
    try:
        if a is None:
            mod = __import__(m, {}, {}, [])
        else:
            mod = getattr(__import__(m, {}, {}, [a]), a)
    except ImportError, e:
        raise ImproperlyConfigured, 'ImportError %s: %s' % (app, e.args[0])

    app_dirs.append(os.path.dirname(mod.__file__))

def get_full_path(request):
    full_path = ('http', ('', 's')[request.is_secure()], '://', request.META['HTTP_HOST'], request.path)
    return ''.join(full_path)

from django.template import RequestContext
def render_template(request, template, context = {}):
    c = RequestContext(request)
    c.update(context)
    ext = os.path.splitext(template)[1]
    template_types = getattr(settings, 'TEMPLATE_TYPES', {})
    if not template_types:
        template_types = {'.mko':'mako'}
    t = ''
    for k, v in template_types.items():
        if k.lower() == ext.lower():
            t = v
            break
        
    if t.lower() == 'mako':
        from mako_django import render_to_response
    else:
        from django.shortcuts import render_to_response
        
    return render_to_response(template, context_instance=c)

def get_func(string):
    module, func = string.rsplit('.', 1)
    mod = __import__(module, {}, {}, [''])
    return getattr(mod, func)

def get_func_args(func, args, kwargs, skip=None):
    import inspect
    v = inspect.getargspec(func)
    k = v[0]
    defaults = v[-1]
    if not defaults:
        defaults = ()
    k1 = k[:-1*len(defaults)]
    if skip is not None:
        k = k[skip:]
        k1 = k1[skip:]
    ks = {}
    for i, p in enumerate(k[:]):
        if p in kwargs:
            ks[p] = kwargs[p]
            del k[i]
            if p in k1:
                k1.remove(p)
    ars = args[:len(k1)]
    return ars, ks

def setting(name, defaultvalue=''):
    from django.conf import settings
    return getattr(settings, name, defaultvalue)

#if __name__ == '__main__':
#    def p(a,b,c=1,d=2):pass
#    args, kwargs = get_func_args(p, (4,5,6), {'b':'a'})
#    print p(*args, **kwargs)
#    