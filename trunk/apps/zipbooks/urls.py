from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    (r'^$', 'apps.zipbooks.views.index'),
    (r'^add/$', 'apps.zipbooks.views.add'),
    (r'^booklist/$', 'apps.zipbooks.views.booklist'),
    (r'^download/(?P<book_id>\d+)/$', 'apps.zipbooks.views.download'),
    (r'^search/$', 'apps.zipbooks.views.search'),
    (r'^monitor/$', 'apps.zipbooks.views.monitor'),
)
