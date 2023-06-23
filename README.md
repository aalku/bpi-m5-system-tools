# bpi-m5-system-tools
System tools for Banana Pi M5.

We currently have a fan controller and a power button controller.

## Dependencies:

### 1. Install needed packages for build and run

```bash
sudo apt install git build-essential python3 python3-dev python3-setuptools python3-evdev
```

### 2. Build and install GPIO Python module.

You can get it from my fork:

- https://github.com/aalku/RPi.GPIO-Amlogic-BPiM5

or from the original from Dangku that currently does not support my BPiM5 on an recent linux kernel:

- https://github.com/Dangku/RPi.GPIO-Amlogic

You can build my fork this way:
```bash
git clone https://github.com/aalku/RPi.GPIO-Amlogic-BPiM5.git
cd RPi.GPIO-Amlogic-BPiM5
sudo python3 setup.py clean --all && sudo python3 setup.py build install
cd -
```

## Services install (systemd)

Enter ``systemd-services`` directory, configure the paths to the python scripts (you can move them somewhere else) and install the services through a link (or you can copy them).

The paths to edit are like this:
```
ExecStart=/usr/bin/python3 /PATH-TO-EDIT/bpi-m5-system-tools/worker-scripts/shutdown-button-controller.py
```

```bash
cd systemd-services

sudo ln -s "$PWD"/*.service /etc/systemd/system/

sudo systemctl enable --now fan-controller
sudo systemctl enable --now shutdown-button-controller

cd -
```