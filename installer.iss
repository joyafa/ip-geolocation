[Setup]
AppId={{A1B2C3D4-1234-5678-ABCD-EF1234567890}
AppName=IP地址归属地查询
AppVersion=1.0.0
AppVerName=IP地址归属地查询 1.0.0
AppPublisher=IP Geolocation
AppPublisherURL=https://github.com
AppSupportURL=https://github.com
DefaultDirName={autopf}\IP地址归属地查询
DefaultGroupName=IP地址归属地查询
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=ip-geolocation-setup
Compression=lzma/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标"
Name: "startupicon"; Description: "创建开始菜单快捷方式"; GroupDescription: "附加图标"

[Files]
Source: "dist\ip-geolocation.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\IP地址归属地查询"; Filename: "{app}\ip-geolocation.exe"; WorkingDir: "{app}"
Name: "{group}\卸载 IP地址归属地查询"; Filename: "{uninstallexe}"
Name: "{autodesktop}\IP地址归属地查询"; Filename: "{app}\ip-geolocation.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\ip-geolocation.exe"; Description: "{cm:LaunchProgram,IP地址归属地查询}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/im ip-geolocation.exe /f"; Flags: runhidden