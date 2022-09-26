Installation
============

Pre-requisites
--------------

The only dependency is `psychopy <https://www.psychopy.org/index.html>`_.
Unfortunately, psychopy itself has a lot of dependencies, some of which are system libraries.

* on Ubuntu 22.04 with Python 3.9 I needed to do
   * ``sudo apt-get install swig libasound2-dev portaudio19-dev libpulse-dev libusb-1.0-0-dev libsndfile1-dev libportmidi-dev liblo-dev libgtk-3-dev``
   * ``pip install wxPython`` (which took a long time to complete - alternative is to install a `pre-built wheel <https://extras.wxpython.org/wxPython4/extras/linux/gtk3/>`_)
   * additionally, at runtime PTB/psychtoolbox needs extra permissions on linux to run
      * short term fix: ``sudo setcap cap_sys_nice=eip /path/to/python/binary``
      * see `this issue <https://discourse.psychopy.org/t/psychopy-keyboard-keyboard-psychhid-kbqueuestart-memory-fault/12005/6>`_

Developer install
-----------------

To clone the repo, make an editable installation and run the tests:

.. code-block:: bash

    git clone https://github.com/ssciwr/motor-task-prototype.git
    cd motor-task-prototype
    pip install -e .[tests,docs]
    xvfb-run pytest

To build the docs (in ``docs/_build/html/index.html``)

.. code-block:: bash

    cd docs
    make
