# motor-task-prototype

Prototype for motor task application

![screenshot](https://raw.githubusercontent.com/ssciwr/motor-task-prototype/main/screenshot.png)

## User Installation

### Windows with standalone Psychopy (recommended)

- Install [StandalonePsychoPy](https://github.com/psychopy/psychopy/releases/download/2022.2.2/StandalonePsychoPy-2022.2.2-win64.exe)
- Download [UpdatePrototype.bat](https://github.com/ssciwr/motor-task-prototype/releases/download/latest/UpdatePrototype.bat) and double-click on it
- Download [RunPrototype.bat](https://github.com/ssciwr/motor-task-prototype/releases/download/latest/RunPrototype.bat) and double-click on it

Notes

- Your browser might warn you about downloading batch files
  - This is normal for a .bat file
  - Click keep -> show more -> keep anyway
- The first time you run it you might get a "Windows protected your PC" message
  - This is also normal for a .bat file
  - Click more info -> run anyway
- What does `UpdatePrototype.bat` do?
  - Running this will install the prototype (or update an existing installation to the latest available version)
  - It runs this command: `"C:\Program Files\PsychoPy\python.exe" -m pip install https://github.com/ssciwr/motor-task-prototype/releases/download/latest/motor_task_prototype-latest-py3-none-any.whl`
  - This installs the latest prototype wheel from Github into your Psychopy Python environment using pip
- What does `RunPrototype.bat` do?
  - This runs the prototype
  - It runs this command: `"C:\Program Files\PsychoPy\python.exe" -m motor_task_prototype`
  - This runs the prototype using your Psychopy Python environment
- If in doubt you can always open the .bat file in notepad to see what commands it will run
- If you have installed Psychopy in a non-default location you will need to update the paths
  in these batch files to point to the psychopy-installed python.exe.

### Alternative pip install

If you already have a Python environment and git you can install using pip:

```
pip install git+https://github.com/ssciwr/motor-task-prototype
```

Note this also installs psychopy with pip, which may need additional
system libraries and configuration steps to work properly,
which is probably why they provide standalone installers for
Psychopy on Windows and Mac which bundle all the requirements.

## Developer Installation

### Pre-requisites

The only dependency is [psychopy](https://www.psychopy.org/index.html).
Unfortunately, psychopy itself has a lot of dependencies, some of which are system libraries.

- on Ubuntu 22.04 with Python 3.10 I needed to do
  - `sudo apt-get install swig libasound2-dev portaudio19-dev libpulse-dev libusb-1.0-0-dev libsndfile1-dev libportmidi-dev liblo-dev libgtk-3-dev`
  - `pip install wxPython` (which took a long time to complete - alternative is to install a [pre-built wheel](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/))
  - additionally, at runtime PTB/psychtoolbox needs extra permissions on linux to run
    - short term fix: `sudo setcap cap_sys_nice=eip /path/to/python/binary`
    - see https://discourse.psychopy.org/t/psychopy-keyboard-keyboard-psychhid-kbqueuestart-memory-fault/12005/6

### Developer install

To clone the repo, make an editable installation and run the tests:

```
git clone https://github.com/ssciwr/motor-task-prototype.git
cd motor-task-prototype
pip install -e .[tests]
pytest
```
