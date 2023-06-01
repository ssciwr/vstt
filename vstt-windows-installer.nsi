# NSIS windows installer to install VSTT using an existing StandalonePsychoPy Python environment
# - https://nsis.sourceforge.io/
# - https://nsis.sourceforge.io/Docs/Modern%20UI%202/Readme.html
# - https://nsis.sourceforge.io/Examples/Modern%20UI/Basic.nsi

!include MUI2.nsh

# general settings
!define VSTT_NAME "Visuomotor Serial Targeting Task"
Name "Visuomotor Serial Targeting Task (VSTT)"
OutFile "vstt-windows-installer.exe"
Unicode True

# pages
!insertmacro MUI_PAGE_WELCOME

!define MUI_PAGE_HEADER_TEXT "Existing PsychoPy installation location"
!define MUI_PAGE_HEADER_SUBTEXT "Please select the location of your existing PsychoPy installation"
!define MUI_DIRECTORYPAGE_TEXT_TOP "If PsychoPy was installed in the default location you should now be able to click 'Install' to install VSTT.$\r$\n$\r$\nIf the Install button is greyed out, no PsychoPy installation was found in the default location below. Please click browse and navigate to the folder where you have installed PsychoPy, then click 'Install'."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Existing PsychoPy installation location"
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES

# languages
!insertmacro MUI_LANGUAGE "English"

# set default psychopy installation location
Function .onInit
    StrCpy $INSTDIR "C:\Program Files\PsychoPy"
FunctionEnd

# validate that selected psychopy folder contains python.exe
Function .onVerifyInstDir
    IfFileExists $INSTDIR\pythonw.exe PathGood
      Abort
    PathGood:
FunctionEnd

# installation
Section "install"
    DetailPrint "PsychoPy installation location: $INSTDIR"
    # pip install vstt using PsychoPy pythonw.exe
    ExecWait '"$INSTDIR\pythonw.exe" -m pip install --upgrade vstt' $0
    ${If} $0 != 0
        messageBox mb_iconstop "Pip install of vstt failed. PsychoPy installation not found at $INSTDIR! Please install StandalonePsychoPy before running this installer, and ensure you have selected the correct location of your PsychoPy installation."
        setErrorLevel 1
        quit
    ${EndIf}
    # desktop shortcut
    CreateShortCut "$DESKTOP\${VSTT_NAME}.lnk" "$INSTDIR\pythonw.exe" "-m vstt" ""
    # startmenu shortcut
    CreateShortCut "$SMPROGRAMS\${VSTT_NAME}.lnk" "$INSTDIR\pythonw.exe" "-m vstt" ""
SectionEnd
