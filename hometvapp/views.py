import json

from django.shortcuts import render
from django.http import HttpResponse

from hometvapp.extras.decorators import onlyxhr

from hometvapp.extras.video import VideoController, VideoOMXPlayerClient, VideoObject

from forms import UploadFileForm

from extras import handle_uploaded_file

# Create your views here.

def index(request):
    videocontroller = VideoController()
    videos = videocontroller.getmultimediafiles()
    return render(request, 'index.html', {'videos': videos,'form': UploadFileForm()})

@onlyxhr
def play(request, slug):
    videocontroller = VideoController()
    video = videocontroller.findvideobyslug(slug)
    videos = videocontroller.getmultimediafiles()
    client = VideoOMXPlayerClient()
    client.play(video)
    return render(request, 'index.html', {'videos': videos})

@onlyxhr
def pause(request):
    videocontroller = VideoController()
    videos = videocontroller.getmultimediafiles()
    client = VideoOMXPlayerClient()
    client.pause()
    return render(request, 'index.html', {'videos': videos})

@onlyxhr
def stop(request):
    videocontroller = VideoController()
    videos = videocontroller.getmultimediafiles()
    client = VideoOMXPlayerClient()
    client.stop()
    return render(request, 'index.html', {'videos': videos})

@onlyxhr
def seek(request, second):
    videocontroller = VideoController()
    videos = videocontroller.getmultimediafiles()
    client = VideoOMXPlayerClient()
    client.seek(second)
    return render(request, 'index.html', {'videos': videos})

@onlyxhr
def current_playing(request):
    client = VideoOMXPlayerClient()
    current_video = client.status()
    jsonreturn = dict()
    jsonreturn['current_playing'] = current_video.getdict() if current_video else {}
    jsonreturn['isplaying'] = client.isplaying()
    return HttpResponse(json.dumps(jsonreturn), content_type='application/json')


def upload_file(request):
    if request.method == 'POST':
        print "UNUTRA"
        form = UploadFileForm(request.POST, request.FILES)
        print form.is_valid()
        if form.is_valid():
            handle_uploaded_file(VideoObject.path, request.FILES['file'])
            return HttpResponse('yay')
    else:
        print "U GETU SAM"
        form = UploadFileForm()
    return HttpResponse("nesto se desilo")
