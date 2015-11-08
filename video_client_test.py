from hometvapp.extras.video import VideoOMXPlayerClient
import time

print "prije"
v = VideoOMXPlayerClient()
print "poslije"

v.send_command("play")

time.sleep(5)

v.send_command("pause")
