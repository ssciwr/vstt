Installation
============

Windows with standalone Psychopy (recommended)
----------------------------------------------

* Install `StandalonePsychoPy <https://github.com/psychopy/psychopy/releases/download/2023.1.2/StandalonePsychoPy-2023.1.2-win64.exe>`_
* Download `UpdateVSTT.bat <https://github.com/ssciwr/vstt/releases/download/latest/UpdateVSTT.bat>`_ and double-click on it
* Download `VSTT.bat <https://github.com/ssciwr/vstt/releases/download/latest/VSTT.bat>`_ and double-click on it

.. note::
   * Your browser might warn you about downloading batch files
      * This is normal for a .bat file
      * Click keep -> show more -> keep anyway
   * The first time you run it you might get a "Windows protected your PC" message
      * This is also normal for a .bat file
      * Click more info -> run anyway
   * What does `UpdateVSTT.bat` do?
      * This installs the latest version of VSTT into your Psychopy Python environment using pip
      * It runs this command: ``"C:\Program Files\PsychoPy\python.exe" -m pip install --upgrade vstt``
   * What does `VSTT.bat` do?
      * This runs VSTT using your Psychopy Python environment
      * It runs this command: ``"C:\Program Files\PsychoPy\python.exe" -m vstt``
   * If in doubt you can always open the .bat file in notepad to see what commands it will run
   * If you have installed Psychopy in a non-default location you will need to update the paths
     in these batch files to point to the psychopy-installed python.exe.

Pip install
-----------

VSTT can also be installed using pip:

``pip install vstt``

.. note::
   On linux the optional psychtoolbox dependency needs permission to set its priority. To allow this:
      * ``sudo setcap cap_sys_nice+ep `python -c "import os; import sys; print(os.path.realpath(sys.executable))"``
   Alternatively you can simply remove psychtoolbox
      * ``pip uninstall psychtoolbox``
