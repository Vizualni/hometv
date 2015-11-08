from __future__ import absolute_import

from celery import shared_task, task
from hometvapp.extras.video import VideoOMXPlayerWrapper

from multiprocessing import Manager

videoplayer = VideoOMXPlayerWrapper()
manager = Manager()
shared = manager.list([videoplayer])


@task
def celery_play(filename):
    shared[0].play(filename)

@task
def celery_pause():
    shared[0].pause()