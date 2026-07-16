!include "MUI2.nsh"

!define APP_NAME "IP Address Lookup"
!define APP_VERSION "1.0.0"
!define APP_EXE "ip-geolocation.exe"
!define APP_DIR "IP Address Lookup"
!define APP_ICON "app.ico"

Name "${APP_NAME}"
OutFile "installer\ip-geolocation-setup.exe"
InstallDir "$PROGRAMFILES\${APP_DIR}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallDir"
RequestExecutionLevel admin

!define MUI_ICON "${APP_ICON}"
!define MUI_UNICON "${APP_ICON}"

!define MUI_WELCOMEPAGE_TITLE "${APP_NAME}"
!define MUI_WELCOMEPAGE_TEXT "${APP_NAME} v${APP_VERSION}\n\nA simple and practical IP address lookup tool\n\nClick Next to continue installation"

!define MUI_DIRECTORYPAGE_TEXT_TOP "Select installation directory"
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Install to:"

!define MUI_FINISHPAGE_TITLE "Installation Complete"
!define MUI_FINISHPAGE_TEXT "${APP_NAME} has been successfully installed\n\nYou can launch the program from desktop shortcut or Start Menu"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File "dist\${APP_EXE}"
  File "${APP_ICON}"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  WriteRegStr HKLM "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
  
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\${APP_ICON}" 0
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk"
  RmDir "$SMPROGRAMS\${APP_NAME}"
  
  ExecWait '"taskkill.exe" /im ${APP_EXE} /f'
  
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\${APP_ICON}"
  Delete "$INSTDIR\uninstall.exe"
  RmDir "$INSTDIR"
  
  DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd

Function .onInstSuccess
FunctionEnd

Function un.onUninstSuccess
FunctionEnd
