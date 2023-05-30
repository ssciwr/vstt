Developer installation
======================

Pre-requisites
--------------

The only dependency is `psychopy <https://www.psychopy.org/index.html>`_.
Unfortunately, psychopy itself has a lot of dependencies, some of which are system libraries.

* on Ubuntu 22.04 with Python 3.9
   * ``sudo apt-get install swig libasound2-dev portaudio19-dev libpulse-dev libusb-1.0-0-dev libsndfile1-dev libportmidi-dev liblo-dev libgtk-3-dev``
   * ``pip install wxPython`` (which took a long time to complete - alternative is to install a `pre-built wheel <https://extras.wxpython.org/wxPython4/extras/linux/gtk3/>`_)
   * additionally, at runtime psychtoolbox needs permission on linux to set its priority:
      * ``sudo setcap cap_sys_nice+ep `python -c "import os; import sys; print(os.path.realpath(sys.executable))"``
   * alternatively simply remove psychtoolbox (it is an optional psychopy dependency):
      * ``pip uninstall psychtoolbox``

Developer install
-----------------

To clone the repo, make an editable installation and run the tests:

.. code-block:: bash

    git clone https://github.com/ssciwr/vstt.git
    cd vstt
    pip install -e .[tests,docs]
    xvfb-run pytest

To build the docs (in ``docs/_build/html/index.html``)

.. code-block:: bash

    cd docs
    make
