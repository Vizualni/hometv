import os
import socket

import pickle
import base64
import json

from hometvapp.extras.omxplayer import OMXPlayerBase, OMXPlayerException

VIDEO_PATH = '/home/pi/video/'

MULTIMEDIA_EXTENSIONS = [
    'mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'mpg',
    'm4v', '3gp', 'webm'
]

def get_all_media_files():
    return ["lala", "misko", "pisko"]

class VideoFolderNotFoundException(Exception):
    pass

class VideoObject(object):
    path = VIDEO_PATH
    def __init__(self, filename, path=VIDEO_PATH):
        """
        TODO: check if filename is really a video (or something omxplayer can play)
        """
        self.__filename = filename
        self.__path = path
        VideoObject.path = path
        self.__slug = str(self.__filename).strip().replace(' ', '-')
        self.__filesize = os.stat(self.getfullpath()).st_size

    def getslug(self):
        return self.__slug

    def getfilename(self):
        return self.__filename

    def getname(self):
        return self.__filename

    def getshortname(self):
        return self.__filename[:10]

    def getpath(self):
        return self.__path

    def getfullpath(self):
        return self.__path + self.__filename

    def rename(self, new_name):
        return os.rename(self.getfullpath(), self.getpath() + new_name)

    def delete(self):
        try:
            return os.remove(self.getfullpath())
        except:
            return "Error while deleting file {}".format(self.getfullpath())

    def __str__(self):
        return "<" + self.getfilename() + ">"

    def __repr__(self):
        return str(self)

    def getdict(self):
        return {
            'slug': self.getslug(),
            'shortname': self.getshortname(),
            'filename': self.getfilename(),
            'size': self.__filesize
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):
        return hash(str(self.getfullpath()) + str(self.__filesize))

    @classmethod
    def serialize(cls, self):
        return base64.b64encode(pickle.dumps(self))

    @classmethod
    def deserialize(cls, self):
        return pickle.loads(base64.b64decode(self))

class VideoController(object):

    def __init__(self, path=VIDEO_PATH):
        self.__check(path)
        self.path = path
        self.__multimedia_list = []

    def __check(self, path):
        if os.path.exists(path) is False:
            raise VideoFolderNotFoundException()

    def getmultimediafiles(self):
        """
        Populate and return all files in path folder
        """
        self.__multimedia_list = []
        for filename in os.listdir(self.path):
            self.__multimedia_list.append(VideoObject(filename, self.path))
        return self.__multimedia_list

    def findvideobyslug(self, slug):
        """
        Finds video by slug
        """
        self.getmultimediafiles()
        for video in self.__multimedia_list:
            if video.getslug() == slug:
                return video
        return None


class VideoOMXPlayerWrapper(object):
    """
    Class that's wrapping to omxplayer class.

    """
    def __init__(self):
        self.omxplayer = OMXPlayer()
        self.status = 0
        self.clients = set([])
        self.videocontroller = VideoController()

    def parse_command(self, command):
        msg = self._parse_command(command)
        return msg

    def _parse_command(self, command):
        command = str(command).strip()
        if str(command).startswith("play "):
            obj = VideoObject.deserialize(command[5:])
            return self.play(obj)
        elif str(command).startswith("playfilename "):
            obj = self.videocontroller.findvideobyslug(command[13:])
            return self.play(obj)
        elif command == "pause":
            return self.pause()
        elif command == "stop":
            return self.stop()
        elif command.startswith("seek "):
            return self.omxplayer.seek(command[5:])
        elif command == "status":
            if self.omxplayer:
                return self.get_omxplayer_current_state()
            return {}
        elif command == "isplaying":
            if self.omxplayer:
                return self.omxplayer.isplaying()
            return False
        elif command.startswith("delete "):
            obj = VideoObject(command[7:])
            obj.delete()
        elif command.startswith("rename "):
            command = command[7:]
            slug, new_name = command.split(' ', 1)
            obj = VideoObject(slug)
            obj.rename(new_name)
        elif command == "toggle_subtitles":
            return self.omxplayer.toggle_subtitles()

    def play(self, video):
        try:
            self.omxplayer.play(video)
        except Exception, e:
            print "lalaexceotuibkurac", e.message

    def pause(self):
        if not self.omxplayer:
            return "No video to pause/resume."
        self.omxplayer.toggle_play()

    def stop(self):
        if self.omxplayer:
            self.omxplayer.stop()
        else:
            return "No video playing to stop it."

    def seek(self, second):
        return "Not implemented yet."
        if self.omxplayer:
            self.omxplayer.seek(second)

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)

    def send_message_to_clients(self, message):
        for client in self.clients:
            client.transport.write(pickle.dumps(message))

    def get_omxplayer_current_state(self):
        state = dict()
        if self.omxplayer and self.omxplayer.current_playing():
            state['isplaying'] = self.omxplayer.isplaying()
            state['VideoObject'] = self.omxplayer.current_playing().getdict()
            state['subtitles'] = self.omxplayer.subtitle_status()
            return state
        return {'isplaying': False}


class SocketClient(object):

    def __init__(self):

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 1234))

    def send_command(self, command, require_output=False):
        return self.__send_command(command, require_output)

    def recv(self, timeout=1):
        oldtimeout = self.client_socket.gettimeout()
        data = None
        try:
            self.client_socket.settimeout(timeout)
            received = self.client_socket.recv(10 * 1024)
            #print "received", received
            data = pickle.loads(received)
        except Exception, e:
            pass
            #print "njiih", e.message
        finally:
            self.client_socket.settimeout(oldtimeout)
        return data

    def __send_command(self, command, require_output):
        self.client_socket.send(command)
        if not require_output:
            return None
        return self.recv(1)

class WebSocketClient(SocketClient):
    """
    Used on websocket server that connects on videoplayer server.
    recv returns json string representing returned value;

     example for no error:
        {'ok': true, ...}

    example for error:
        {'error': 'error message'}
    """
    def recv(self, timeout=1):
        try:
            response = super(WebSocketClient, self).recv(timeout)
            if response is None:
                return None
            if isinstance(response, VideoObject):
                response = {'VideoObject': response.getdict()}
            return json.dumps({'ok': True, 'data': response})
        except Exception, e:
            return json.dumps({'error': 'Error while talking with video player server: {}'.format(e.message)})


class VideoOMXPlayerClient():

    def __init__(self):
        self.client = SocketClient()

    def play(self, videoobj):
        self.client.send_command("play " + VideoObject.serialize(videoobj))

    def playfilename(self, videopath):
        self.client.send_command("playfilename " + videopath)

    def pause(self):
        self.client.send_command("pause")

    def stop(self):
        self.client.send_command("stop")

    def seek(self, second):
        self.client.send_command("seek " + second)

    def status(self):
        video_base64 = self.client.send_command("status", True)
        if not video_base64:
            return None
        return None

    def isplaying(self):
        val = self.client.send_command("isplaying", True)
        return {'isplaying': True if val else False }


class OMXPlayer(OMXPlayerBase):

    def __init__(self):
        super(OMXPlayer, self).__init__()
        self.current_video_playing = None

    def play(self, video):
        if not isinstance(video, VideoObject):
            raise OMXPlayerException("argument video must be VideoObject")
        self.current_video_playing = video
        super(OMXPlayer, self).play(self.current_video_playing.getfullpath())

    def current_playing(self, for_json=False):
        if for_json:
            if self.current_video_playing:
                return self.current_video_playing.getdict()
        return self.current_video_playing

    def stop(self):
        self.current_video_playing = None
        return super(OMXPlayer, self).stop()



