import signal
import time
import RPi.GPIO as GPIO  
import datetime
import json

# Define the GPIO pin that connects the fan
fanPin = 23    # pin 16 (bcm27)

# Config
# temp C, on at maxTemp and off below lowTemp
maxTemp = 55
lowTemp = 45

# Sensor file
sensorFile = "/sys/class/thermal/thermal_zone0/temp"

# Status file, so other apps can tell if it's on or off. Set it to False to disable
statusFile = "/run/fan-status.json"

# FANcy startup and shutdown with a fan pulse
fancyStart = True
fancyShutdown = True

def exit_gracefully(self, *args):
    raise BaseException("Shutting down")

def setup():
    if (lowTemp >= maxTemp):
        raise BaseException("lowTemp must be lower than maxTemp")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fanPin, GPIO.OUT)
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    if (fancyStart):
        set(True, readTemperature())
        time.sleep(2)
        set(False, readTemperature())
        time.sleep(1)
    else:
        set(False, readTemperature())

def shutdown():
    try:
        if (fancyShutdown):
            set(True, "?")
            time.sleep(2)
            set(False, "?")
        else:
            set(False, "?")
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

def saveStatus(fan, temp):
    if statusFile:
        f = open(statusFile, "wt")
        try:
            f.write(json.dumps({
                "state": fan,
                "temp-c": temp,
                "updated-ts": datetime.datetime.now().isoformat()
            }))
            f.write("\n")
        finally:
            f.close()


def set(fan, temp):
    GPIO.output(fanPin, GPIO.HIGH if fan else GPIO.LOW)
    saveStatus(fan, temp)

# Program start
if __name__ == '__main__':
    setup()
    try:
        while True:
            temp = readTemperature()
            if temp >= maxTemp:
                set(True, temp)
            elif temp <= lowTemp:
                set(False, temp)
            time.sleep(10)
    finally:
        shutdown()