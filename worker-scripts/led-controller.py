import signal
import time

# The main purpose of this service is to keep the leds off so they don't disturb anyone at night.
# It also use the leds to signal startup and shutdown setting the green led on as soon as possible
#  after boot and then off after a few seconds and then the blue led at shutdown until real power off.
# In the next boot (resumed) it might start blue until the service is restarted.

leds = { 
    "ledBoot": "/sys/class/leds/green:status",
    "ledShutdown": "/sys/class/leds/blue:status" 
}

def writeToFile(led, file, content):
    f = open(leds[led] + "/" + file, "w")
    try:
        f.write(str(content))
    finally:
        f.close()

def set(led, brightness=0):
    writeToFile(led, "trigger", "none")
    writeToFile(led, "brightness", brightness)

def shutdown():
    set("ledBoot", 0)
    set("ledShutdown", 255)

def exit_gracefully(self, *args):
    shutdown()
    exit(0)

def startUp():
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    set("ledBoot", 255)
    set("ledShutdown", 0)
    time.sleep(3)
    set("ledBoot", 0)

# Program start
if __name__ == "__main__":
    startUp()
    while True:
        time.sleep(10)

