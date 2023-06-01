Installation
============

Windows with standalone Psychopy (recommended)
----------------------------------------------

For windows users the recommended way to install VSTT is to
first install StandalonePsychoPy, then use the VSTT windows installer:

1. Install `StandalonePsychoPy <https://github.com/psychopy/psychopy/releases/download/2023.1.2/StandalonePsychoPy-2023.1.2-win64.exe>`_
2. Install `VSTT <https://github.com/ssciwr/vstt/releases/download/latest/vstt-windows-installer.exe>`_

Pip install
-----------

VSTT can also be installed using pip:

``pip install vstt``

.. note::
   On linux the optional psychtoolbox dependency needs permission to set its priority. To allow this:
      * ``sudo setcap cap_sys_nice+ep `python -c "import os; import sys; print(os.path.realpath(sys.executable))"``
   Alternatively you can simply remove psychtoolbox
      * ``pip uninstall psychtoolbox``
