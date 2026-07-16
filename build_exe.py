import subprocess
import sys
import os

def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(project_dir, 'app.py')
    db_path = os.path.join(project_dir, 'GeoLite2-City.mmdb')
    
    if not os.path.exists(db_path):
        print(f"Error: GeoLite2-City.mmdb not found at {db_path}")
        sys.exit(1)
    
    exclude_modules = [
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'IPython', 'jedi', 'parso', 'pygments',
        'PIL', 'cryptography', 'bcrypt', 'traitlets',
        'tkinter', 'unittest', 'test', 'doctest',
        'xmlrpc', 'smtpd', 'ftplib',
        'cgi', 'cgitb'
    ]
    
    icon_path = os.path.join(project_dir, 'app.ico')
    
    cmd = [
        'pyinstaller',
        '--name', 'ip-geolocation',
        '--onefile',
        '--windowed',
        '--add-data', f'{db_path};.',
        '--icon', icon_path,
        '--hidden-import', 'flask',
        '--hidden-import', 'flask.json',
        '--hidden-import', 'maxminddb',
        '--hidden-import', 'requests',
        '--hidden-import', 'ipaddress',
        '--hidden-import', 'webview',
        '--hidden-import', 'webview.platforms.winforms',
        '--hidden-import', 'clr_loader',
        '--hidden-import', 'pythonnet',
        '--clean',
        '-y'
    ]
    
    for mod in exclude_modules:
        cmd.extend(['--exclude-module', mod])
    
    cmd.append(app_path)
    
    print('Building executable...')
    print('Command:', ' '.join(cmd))
    
    result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
    
    if result.returncode == 0:
        print('\nBuild succeeded!')
        exe_path = os.path.join(project_dir, 'dist', 'ip-geolocation.exe')
        print(f'Executable created at: {exe_path}')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f'File size: {size_mb:.2f} MB')
    else:
        print('\nBuild failed!')
        print('stdout:', result.stdout)
        print('stderr:', result.stderr)
        sys.exit(1)

if __name__ == '__main__':
    build()