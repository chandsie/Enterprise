from django.conf.urls.defaults import *
from django.contrib import admin
import os

admin.autodiscover()

site_media = os.path.join(os.path.dirname(__file__), 'site_media')


urlpatterns = patterns('',
    (r'^', include('Enterprise.logger.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root' : site_media}),
)
