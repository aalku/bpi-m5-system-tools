import time
import evdev, signal, os

# Config
shutdownCommand = "sudo shutdown now"
buttonName = "BTN_3"
devicePath = "/dev/input/by-path/platform-adc_keys-event"

def exit_gracefully(self, *args):
    raise BaseException("Shutting down")


def setup():
    global dev
    global keyCode
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    dev = evdev.InputDevice(devicePath)
    keyCode = evdev.ecodes.ecodes[buttonName]
    # print ("key code is " + str(key))


# Program start
if __name__ == "__main__":
    setup()
    try:
        ignoreUntil = time.time()  # so we can ignore events in certain conditions like previous events, for starters
        for event in dev.read_loop():
            if event.timestamp() > ignoreUntil and event.type == evdev.ecodes.EV_KEY and event.code == keyCode and event.value > 0:
                # print(evdev.categorize(event))
                # print(event.code)
                # print(event.value)
                print("Shutdown key was pressed")
                os.system(shutdownCommand)
                ignoreUntil = time.time() + 10  # ignore events for x seconds.
                # Probably this script is aborted before that time but just in case we don't exit unless systemd kills us
    finally:
        pass
