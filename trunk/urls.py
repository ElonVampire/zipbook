from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    (r'^zipbooks/', include('apps.zipbooks.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^site_media/(.*)$', 'utils.staticview.serve', {'document_root': settings.SITE_MEDIA, 'app_media_folder':'media'}),
    
)
