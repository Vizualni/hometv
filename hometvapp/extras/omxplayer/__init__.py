import subprocess
import time
import os

from threading import Thread
import Queue
#from hometvapp.extras.video import VideoObject

class ProcessCommunicator(Thread):

    queue = Queue.Queue()

    def __init__(self, arguments=[]):
        super(ProcessCommunicator, self).__init__()
        ProcessCommunicator.queue.empty()
        self.proc = subprocess.Popen(
            arguments,
            stdin=subprocess.PIPE,
            stdout=open(os.devnull, 'wb'),
            close_fds=True
        )

    def send_command(self, command, output=False):
        ProcessCommunicator.queue.put((command, output))

    def isProcessAlive(self):
        if not self.proc:
            return False
        return True if not self.proc.poll() else False

    def kill(self):

        if self.proc:
            ProcessCommunicator.queue.put((None, False))
            time.sleep(1)
            try:
                killall = subprocess.Popen(
                    ['pkill', '-9', 'omxplayer'],
                    close_fds=True
                )
                time.sleep(1)
            except Exception, e:
                print e.message
                self.proc.terminate()
                self.proc.kill()
            finally:
                self.proc = None

    def run(self):

        while True:
            try:
                command, output = ProcessCommunicator.queue.get(timeout=1)
            except Queue.Empty, e:
                if not self.isProcessAlive():
                    break
                else:
                    continue
            if not command:
                break
            try:
                self.proc.stdin.write(command)
                self.proc.stdin.flush()
            except Exception, e:
                print e.message
            ProcessCommunicator.queue.task_done()

class OMXPlayerException(Exception):
    pass

class OMXPlayerBase(object):

    def __init__(self):
        self.proc = None
        self.playing = False
        self.subtitles = False

    def play(self, filename):
        if self.proc:
            self.kill()
        self.proc = ProcessCommunicator(['/usr/bin/omxplayer', '-b', '-r', '-o', 'hdmi', filename])
        self.proc.daemon = True
        self.proc.start()
        self.playing = True
        self.subtitles = False

    def toggle_play(self):
        if self.proc.isProcessAlive():
            self.proc.send_command('p')
            self.playing = not self.playing

    def toggle_subtitles(self):
        if self.proc.isProcessAlive():
            self.proc.send_command('s')
            self.subtitles = not self.subtitles

    def stop(self):
        if self.proc:
            self.kill()

    def kill(self):
        if self.proc:
            self.proc.kill()
            print "cekam da umre"
            self.proc.join()
            print "umro!"
            self.proc = None

    def isplaying(self):
        return self.playing

    def subtitle_status(self):
        return self.subtitles

    def seek(self, value):
        key_value = {'l': "\x1B[D", 'r': "\x1B[C", 'll': "\x1B[B", 'rr': "\x1B[A"}
        print value
        if self.proc:
            if value in key_value.keys():
                return self.proc.send_command(key_value[value])