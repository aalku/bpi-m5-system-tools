import signal
import time
import RPi.GPIO as GPIO
import datetime
import json

# Define the GPIO pin that connects the fan
fanPin = 23  # pin 16 (bcm27)

# Config
# temp C, on at maxTemp and off below lowTemp
maxTemp = 65
lowTemp = 55

# Sensor file
sensorFile = "/sys/class/thermal/thermal_zone0/temp"

# Status file, so other apps can tell if it's on or off. Set it to False to disable
statusFile = "/run/fan-status.json"

# Log file. Every line is a JSON object. Set it to False to disable
logFile = "/var/log/fan-controller.log"
logEveryMinutes = 2

# FANcy startup and shutdown with a fan pulse
fancyStart = True
fancyShutdown = True

# Status for log. This is not configuration
status = {
    "lastLogTimestamp": 0,
    "lastLogStatus": None,
    "lastLogTemperature" : None,
    "lastLogComment" : None,
    "lastStatus" : None
}

def exit_gracefully(self, *args):
    raise BaseException("Shutting down")


def setup():
    if lowTemp >= maxTemp:
        raise BaseException("lowTemp must be lower than maxTemp")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fanPin, GPIO.OUT)
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    if fancyStart:
        set(True, readTemperature(), "fancy start (previous to boot)")
        time.sleep(2)
        set(False, readTemperature(), "boot")
        time.sleep(1)
    else:
        set(False, readTemperature(), "boot")


def shutdown():
    try:
        if fancyShutdown:
            set(True, "?", "fancy shutdown")
            time.sleep(2)
            set(False, "?", "shutdown")
        else:
            set(False, "?", "shutdown")
    finally:
        GPIO.setup(fanPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.cleanup()


def readTemperature():
    f = open(sensorFile, "r")
    try:
        temp = f.read()
    finally:
        f.close()
    # Divide by 1000 to get the temperature in degrees Celsius
    temp = int(temp) / 1000
    return temp


def saveStatus(fan, temp, comment = None):
    try:
        if statusFile:
            f = open(statusFile, "wt")
            try:
                f.write(
                    json.dumps(
                        {
                            "state": fan,
                            "temp-c": temp,
                            "updated-ts": datetime.datetime.now().isoformat(),
                            "comment": comment,
                        }
                    )
                    + "\n"
                )
            finally:
                f.close()
    finally:
        status["lastStatus"] = fan


def log(fan, temp, comment = None):
    global status
    if logFile and logEveryMinutes:
        
        minutesSinceLog = (datetime.datetime.now().timestamp() - status["lastLogTimestamp"])  / 60
        stateChange = fan != status["lastLogStatus"]
        bigTempChange = (status["lastLogTemperature"] == "?") != (temp == "?")
        commentChange = comment != status["lastLogComment"]

        if (stateChange or bigTempChange or minutesSinceLog >= logEveryMinutes or commentChange):
            status["lastLogStatus"] = fan
            status["lastLogTimestamp"] = datetime.datetime.now().timestamp()
            status["lastLogTemperature"] = temp
            status["lastLogComment"] = comment
            f = open(logFile, "a")
            try:
                f.write(
                    json.dumps(
                        {
                            "updated-ts": datetime.datetime.now().isoformat(),
                            "temp-c": temp,
                            "state": fan,
                            "comment": comment
                        }
                    )
                    + "\n"
                )
            finally:
                f.close()


def set(fan, temp, comment = None):
    GPIO.output(fanPin, GPIO.HIGH if fan else GPIO.LOW)
    saveStatus(fan, temp, comment)
    log(fan, temp, comment)


# Program start
if __name__ == "__main__":
    setup()
    try:
        while True:
            temp = readTemperature()
            if temp >= maxTemp:
                set(True, temp, "over maxTemp " + str(maxTemp))
            elif temp <= lowTemp and status["lastStatus"] != False:
                set(False, temp, "under lowTemp " + str(lowTemp))
            elif status["lastStatus"]:
                set(True, temp, "still over lowTemp " + str(lowTemp))
            else:
                set(False, temp, "")
            time.sleep(10)
    finally:
        shutdown()
