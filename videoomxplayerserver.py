from twisted.internet import protocol, reactor, endpoints
from hometvapp.extras.video import VideoOMXPlayerWrapper
from hometvapp.extras import FolderListener
import pickle
import json

video = VideoOMXPlayerWrapper()
folderlistener = FolderListener()

def callback(folders):
    to_json = {'folders': [v.getdict() for v in folders]}
    video.send_message_to_clients(to_json)

folderlistener.setcallbackevent(callback)
folderlistener.start()

class Video(protocol.Protocol):

    clientcounter = 0

    def connectionMade(self):
        Video.clientcounter+=1
        video.add_client(self)
        print "New client connected (counter " + str(Video.clientcounter) + ")"
        callback(folderlistener.get_current_folder_status())

    def connectionLost(self, reason=None):
        Video.clientcounter-=1
        video.remove_client(self)
        print "Client disconnected (counter " + str(Video.clientcounter) + ")"

    def dataReceived(self, data):
        data = data.strip()
        print "Client poslao: " + data[:50]
        res = video.parse_command(data)
        if res:
            video.send_message_to_clients(res)
        else:
            video.send_message_to_clients(video.parse_command("status"))
        #self.transport.write(pickle.dumps(res))

class VideoFactor(protocol.Factory):

    def buildProtocol(self, addr):
        return Video()

endpoints.serverFromString(reactor, "tcp:1234").listen(VideoFactor())
reactor.run()