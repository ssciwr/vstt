# motor-task-prototype

Prototype for motor task application

## Installation

### Pre-requisites

The only dependency is [psychopy](https://www.psychopy.org/index.html).
Unfortunately, psychopy itself has a lot of dependencies, some of which are system libraries.

- on Ubuntu 22.04 with Python 3.10 I needed to do
  - `sudo apt-get install swig libasound2-dev portaudio19-dev libpulse-dev libusb-1.0-0-dev libsndfile1-dev libportmidi-dev liblo-dev libgtk-3-dev`
  - `pip install wxPython` (which took a long time to complete)
  - additionally, at runtime psychtoolbox needs extra permissions on linux to run
    - short term fix: `sudo setcap cap_sys_nice=eip /path/to/python/binary`
    - see https://discourse.psychopy.org/t/psychopy-keyboard-keyboard-psychhid-kbqueuestart-memory-fault/12005/6
- on windows
  - with python 3.8 pip install on CI just worked without any further dependencies
  - note: this has not been verified on a clean Windows machine

### User installation

To install using pip:

```
pip install git+https://github.com/ssciwr/motor-task-prototype
```

### Developer install

To clone the repo, make an editable installation and run the tests:

```
git clone https://github.com/ssciwr/motor-task-prototype.git
cd motor-task-prototype
pip install -e .[tests]
pytest
```
