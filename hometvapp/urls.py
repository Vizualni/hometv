from django.conf.urls import include, url
from views import index, play, pause, stop, seek, current_playing, upload_file

urlpatterns = [
    url(r'^$', index),
    url(r'^play/(?P<slug>[a-zA-Z0-9\.\-]+)', play),
    url(r'^pause', pause),
    url(r'^stop', stop),
    url(r'^seek/(?P<second>[\d]+)', seek),
    url(r'^current_playing', current_playing),
    url(r'^upload', upload_file)
]
