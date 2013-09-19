from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^', include('howtostoreiosdata.wizard.urls', namespace="wizard")),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
