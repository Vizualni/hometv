#!/usr/bin/env python
import sys
import time
from hometvapp.extras.video import WebSocketClient
from threading import Thread
import Queue
client = WebSocketClient()
out_queue = Queue.Queue()

def d(m):
    sys.stderr.write(str(m))
    sys.stderr.flush()

def input_thread():
    while True:
        inp = raw_input()
        client.send_command(inp)

def output_thread():
    while True:
        try:
            item = out_queue.get()
        except Queue.Empty, e:
            continue
        #print ("outputano " + str(item))
        print item
        sys.stdout.flush()
        out_queue.task_done()

def waiting_thread():
    while True:
        inp = client.recv(10)
        #print ("samo doslo " + str(inp))
        if not inp:
            continue
        out_queue.put(inp)

threads = [Thread(target=input_thread), Thread(target=output_thread), Thread(target=waiting_thread)]

try:
    for t in threads:
        t.daemon = True
        t.start()


    while True:
        time.sleep(100)
except (KeyboardInterrupt, SystemExit):
    pass


