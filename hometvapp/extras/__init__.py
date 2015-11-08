__author__ = 'Vizualni'
import os
import time
from video import VIDEO_PATH, VideoObject
from threading import Thread



def handle_uploaded_file(folder, filerequest):
    with open(folder + filerequest.name, 'wb+') as destination:
        for chunk in filerequest.chunks():
            destination.write(chunk)

class FolderListener(Thread):

    def __init__(self, folder=VIDEO_PATH, timeout=1, cast_object=VideoObject):

        super(FolderListener, self).__init__()
        self.__folder = folder
        self.__timeout = timeout
        self.running = True
        self.daemon = True
        self.__previous_folder = []
        self.__cast_object = cast_object
        self.__callback_event = None

    def exit(self):
        self.running = False

    def setcallbackevent(self, callback_event):
        assert hasattr(callback_event, '__call__')
        self.__callback_event = callback_event

    def run(self):
        while self.running:
            time.sleep(self.__timeout)
            current_folder = [self.__cast_object(x) for x in os.listdir(self.__folder)]
            if set(current_folder) == set(self.__previous_folder):
                # nothing to do. no change was in the folders
                continue
            #print current_folder
            copy = list(current_folder)
            self.__callback_event(copy)
            self.__previous_folder = list(copy)

    def get_current_folder_status(self):
        return list(self.__previous_folder)